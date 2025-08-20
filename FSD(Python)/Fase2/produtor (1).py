import json
import requests
import threading
from flask import Flask, jsonify, request
from datetime import datetime
import time
import socket

# Configurações do Produtor
PRODUTOR_IP = "0.0.0.0"
PRODUTOR_PORT = 5000
GESTOR_IP = "193.136.11.170"
GESTOR_PORT = 5001
PRODUTOR_NOME = "Produtor_A"

# Configurações específicas de cada produtor (diferentes listas de produtos)
PRODUTORES = {
    ('127.0.0.1', 65432): [
        {"categoria": "Fruta", "produto": "maçã", "quantidade": 100, "preco": 0.5},
        {"categoria": "Legume", "produto": "cenoura", "quantidade": 60, "preco": 0.4}
    ],
    ('127.0.0.1', 65433): [
        {"categoria": "Fruta", "produto": "banana", "quantidade": 80, "preco": 0.3},
        {"categoria": "Legume", "produto": "tomate", "quantidade": 50, "preco": 0.7}
    ],
    ('127.0.0.1', 65434): [
        {"categoria": "Fruta", "produto": "laranja", "quantidade": 50, "preco": 0.5},
        {"categoria": "Legume", "produto": "pimento", "quantidade": 45, "preco": 0.4}
    ],
    (PRODUTOR_IP, PRODUTOR_PORT): [
        {"categoria": "Roupa", "produto": "camisola", "quantidade": 35, "preco": 3},
        {"categoria": "Sapatos", "produto": "sapatilha", "quantidade": 20, "preco": 60}
    ]
}

# Inicializar o servidor Flask
app = Flask(__name__)
produtos = PRODUTORES.get((PRODUTOR_IP, PRODUTOR_PORT), [])

# Função para registar o produtor no Gestor de Produtores
def registar_produtor():
    url = f"http://{GESTOR_IP}:{GESTOR_PORT}/produtor"
    dados = {
        "ip": PRODUTOR_IP,
        "porta": PRODUTOR_PORT,
        "nome": PRODUTOR_NOME
    }
    try:
        response = requests.post(url, json=dados)
        if response.status_code in [200, 201]:
            print(f"Produtor registado com sucesso no Gestor. Status: {response.status_code}")
        else:
            print(f"Falha ao registar no Gestor. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar-se ao Gestor: {e}")

# Registro periódico do produtor
def registar_periodicamente():
    while True:
        registar_produtor()
        time.sleep(300)

# Endpoint para listar categorias de produtos
@app.route("/categorias", methods=["GET"])
def listar_categorias():
    categorias = list({produto["categoria"] for produto in produtos})
    return jsonify(categorias), 200

# Endpoint para listar produtos por categoria
@app.route("/produtos", methods=["GET"])
def listar_produtos():
    categoria = request.args.get("categoria")
    if not categoria:
        return jsonify({"erro": "Categoria não especificada"}), 400
    produtos_categoria = [p for p in produtos if p["categoria"].lower() == categoria.lower()]
    if not produtos_categoria:
        return jsonify({"erro": "Categoria Inexistente"}), 404
    return jsonify(produtos_categoria), 200

# Endpoint para comprar um produto específico
@app.route("/comprar/<produto>/<int:quantidade>", methods=["GET"])
def comprar_produto(produto, quantidade):
    for p in produtos:
        if p["produto"].lower() == produto.lower():
            if p["quantidade"] < quantidade:
                return jsonify({"erro": "Quantidade indisponível"}), 404
            p["quantidade"] -= quantidade
            return jsonify({"mensagem": "Produtos comprados"}), 200
    return jsonify({"erro": "Produto inexistente"}), 404

# Função para iniciar produtor TCP
def iniciar_produtor_tcp(host, port):
    produtos_tcp = PRODUTORES.get((host, port), [])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f'Produtor TCP disponível em {host}:{port}')
        
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_marketplace, args=(conn, produtos_tcp)).start()

# Função para lidar com pedidos TCP
def handle_marketplace(conn, produtos_tcp):
    try:
        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break

            operacao, *args = data.split()

            if operacao == 'LISTAR':
                if len(args) == 0:
                    categorias = list({produto["categoria"] for produto in produtos_tcp})
                    resposta = "Categorias disponíveis: " + ", ".join(categorias) if categorias else "Nenhuma categoria disponível."
                    conn.sendall(resposta.encode('utf-8'))
                else:
                    categoria = args[0]
                    produtos_categoria = [f"{p['produto']},{p['quantidade']},{p['preco']}" for p in produtos_tcp if p["categoria"].lower() == categoria.lower()]
                    resposta = ";".join(produtos_categoria) if produtos_categoria else "Nenhum produto encontrado."
                    conn.sendall(resposta.encode('utf-8'))

            elif operacao == 'COMPRAR':
                if len(args) < 2:
                    conn.sendall("Erro: Pedido inválido.".encode('utf-8'))
                    continue
                
                produto, quantidade = args[0], int(args[1])
                for p in produtos_tcp:
                    if p["produto"].lower() == produto.lower():
                        if p["quantidade"] < quantidade:
                            conn.sendall(f"Erro: Quantidade insuficiente para {produto}.".encode('utf-8'))
                        else:
                            p["quantidade"] -= quantidade
                            conn.sendall(f"Compra realizada: {quantidade}x {produto}.".encode('utf-8'))
                        break
                else:
                    conn.sendall(f"Erro: Produto {produto} não encontrado.".encode('utf-8'))
            else:
                conn.sendall("Erro: Operação desconhecida.".encode('utf-8'))
    except Exception as e:
        print(f"Erro: {e}")
        conn.sendall("Erro interno.".encode('utf-8'))
    finally:
        conn.close()

# Iniciar servidores e threads
def iniciar_produtores():
    for host, port in PRODUTORES:
        if (host, port) != (PRODUTOR_IP, PRODUTOR_PORT):
            threading.Thread(target=iniciar_produtor_tcp, args=(host, port)).start()

if __name__ == "__main__":
    threading.Thread(target=registar_periodicamente, daemon=True).start()
    iniciar_produtores()
    app.run(host=PRODUTOR_IP, port=PRODUTOR_PORT)

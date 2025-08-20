import json
import requests
import threading
from flask import Flask, jsonify, request
from datetime import datetime
import time
import socket

# Configurações para o servidor do Produtor
PRODUTOR_IP = "0.0.0.0"  # IP do Produtor
PRODUTOR_PORT = 5000  # Porta do Produtor
GESTOR_IP = "193.136.11.170"  # IP do Gestor de Produtores
GESTOR_PORT = 5001  # Porta do Gestor de Produtores
PRODUTOR_NOME = "Produtor_A"  # Nome do Produtor (mude conforme necessário)

# Lista de configurações de produtores (diferentes IPs e portas)
PRODUTORES_Socket = [
    ('127.0.0.1', 65432),  # Produtor 1
    ('127.0.0.1', 65433),  # Produtor 2
    ('127.0.0.1', 65434),  # Produtor 3 (Adicionar mais produtores conforme necessário)
]

# Inicializar a lista de produtos e o servidor Flask
app = Flask(__name__)
produtos = [
    {"categoria": "Fruta", "produto": "Maçã", "quantidade": 50, "preco": 1.5},
    {"categoria": "Roupa", "produto": "Camiseta", "quantidade": 20, "preco": 10.0},
    # Adicione outros produtos conforme necessário
]

# Função para registrar o produtor no Gestor de Produtores
def registrar_produtor():
    url = f"http://{GESTOR_IP}:{GESTOR_PORT}/produtor"
    dados = {
        "ip": PRODUTOR_IP,
        "porta": PRODUTOR_PORT,
        "nome": PRODUTOR_NOME
    }
    try:
        response = requests.post(url, json=dados)
        if response.status_code in [200, 201]:
            print(f"Produtor registrado com sucesso no Gestor. Status: {response.status_code}")
        else:
            print(f"Falha ao registrar no Gestor. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar-se ao Gestor: {e}")

# Registro periódico do produtor no Gestor de Produtores
def registrar_periodicamente():
    while True:
        registrar_produtor()
        time.sleep(300)  # Reenviar o registro a cada 5 minutos

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

# Endpoint para comprar uma quantidade específica de um produto
@app.route("/comprar/<produto>/<int:quantidade>", methods=["GET"])
def comprar_produto(produto, quantidade):
    for p in produtos:
        if p["produto"].lower() == produto.lower():
            if p["quantidade"] < quantidade:
                return jsonify({"erro": "Quantidade indisponível"}), 404
            p["quantidade"] -= quantidade
            return jsonify({"mensagem": "Produtos comprados"}), 200
    return jsonify({"erro": "Produto inexistente"}), 404

# Função para lidar com os pedidos do Marketplace
def handle_marketplace(conn):
    try:
        while True:
            # Receber pedido do Marketplace
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            
            # Tratar o pedido
            operacao, *args = data.split()

            if operacao == 'LISTAR':
                # Marketplace pediu a lista de produtos para certas categorias
                categorias = args
                lista = listar_produtos(categorias)
                conn.sendall(str(lista).encode('utf-8'))

            elif operacao == 'COMPRAR':
                # Marketplace pediu para comprar um produto
                produto = args[0]
                quantidade = int(args[1])
                sucesso = comprar_produto(produto, quantidade)
                if sucesso:
                    conn.sendall(f'Compra de {quantidade}x {produto} efetuada.'.encode('utf-8'))
                else:
                    conn.sendall(f'Falha ao comprar {produto}. Stock insuficiente ou produto inexistente.'.encode('utf-8'))
    finally:
        conn.close()

# Iniciar o servidor Produtor em uma porta específica
def iniciar_produtor(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f'Produtor disponível em {host}:{port}')
        
        while True:
            conn, addr = server_socket.accept()
            print(f'Marketplace conectado: {addr}')
            threading.Thread(target=handle_marketplace, args=(conn,)).start()

# Iniciar múltiplos produtores em threads diferentes
def iniciar_produtores():
    for host, port in PRODUTORES_Socket:
        threading.Thread(target=iniciar_produtor, args=(host, port)).start()

# Inicializar o servidor Flask
if __name__ == "__main__":

    iniciar_produtores()

    # Iniciar a thread para registro periódico no Gestor de Produtores
    threading.Thread(target=registrar_periodicamente, daemon=True).start()
    
    # Iniciar o servidor Flask
    app.run(host=PRODUTOR_IP, port=PRODUTOR_PORT)
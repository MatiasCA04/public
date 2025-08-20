import base64
import requests
import socket
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

# Caminho para a chave pública do Gestor
CAMINHO_CHAVE_PUBLICA_GESTOR = "manager_public_key.pem"

# URL do Gestor de Produtores
URL_GESTOR = "http://193.136.11.170:5001/produtor"

# Função para carregar a chave pública do Gestor
def carregar_chave_publica_gestor():
    with open(CAMINHO_CHAVE_PUBLICA_GESTOR, "rb") as f:
        chave_publica = RSA.import_key(f.read())
    return chave_publica

# Validar o certificado com PKCS1v15
def validar_certificado(certificado, chave_publica_gestor):
    hash_certificado = SHA256.new(certificado.encode('utf-8'))
    try:
        PKCS115_SigScheme(chave_publica_gestor).verify(hash_certificado, certificado)
        print("Certificado válido.")
        return True
    except (ValueError, TypeError):
        print("Certificado inválido.")
        return False

# Validar a assinatura digital com PSS
def validar_assinatura(mensagem, assinatura, chave_publica_produtor):
    hash_mensagem = SHA256.new(mensagem.encode('utf-8'))
    try:
        pss.new(chave_publica_produtor).verify(hash_mensagem, assinatura)
        print("Assinatura válida.")
        return True
    except (ValueError, TypeError):
        print("Assinatura inválida.")
        return False

# Enviar pedido seguro ao Produtor e validar resposta
def enviar_pedido_seguro(ip, porta, operacao, *args):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, porta))
            mensagem = json.dumps({"operacao": operacao, "args": args})
            s.sendall(mensagem.encode('utf-8'))

            # Receber resposta
            data = s.recv(4096).decode('utf-8')
            resposta = json.loads(data)

            mensagem = resposta["mensagem"]
            assinatura = base64.b64decode(resposta["assinatura"])
            certificado = resposta["certificado"]

            # Carregar chave pública do Gestor
            chave_publica_gestor = carregar_chave_publica_gestor()

            # Validar certificado
            if not validar_certificado(certificado, chave_publica_gestor):
                print("Certificado inválido.")
                return None

            # Carregar chave pública do Produtor a partir do certificado
            chave_publica_produtor = RSA.import_key(certificado)

            # Validar assinatura
            if not validar_assinatura(mensagem, assinatura, chave_publica_produtor):
                print("Assinatura inválida.")
                return None

            # Retornar a mensagem válida
            return mensagem
        except Exception as e:
            print(f"Erro ao conectar-se ao produtor: {e}")
            return None

# Obter produtores REST do Gestor
def obter_produtores_rest():
    try:
        resposta = requests.get(URL_GESTOR)
        if resposta.status_code == 200:
            produtores_rest = resposta.json()
            for produtor in produtores_rest:
                produtor["tipo"] = "REST"
            return produtores_rest
        else:
            print(f"Erro ao obter produtores REST: {resposta.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar-se ao Gestor: {e}")
        return []
    
# Função para obter categorias via socket TCP
def obter_categorias_tcp(ip, porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, porta))
            s.sendall(b"LISTAR")  # Envia o pedido de listar categorias
            data = s.recv(1024).decode('utf-8').strip()
            
            # Verificar se a resposta não está vazia
            if data:
                categorias = data.split(': ')[1].split(', ')
                print(f"Categorias disponíveis: {', '.join(categorias)}")
                return categorias
            else:
                print("Nenhuma categoria disponível.")
                return []
        except Exception as e:
            print(f"Erro ao conectar-se ao produtor TCP: {e}")
            return []

# Função para obter produtos de uma categoria via socket TCP
def obter_produtos_tcp(ip, porta, categoria):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, porta))
            mensagem = f"LISTAR {categoria}"
            s.sendall(mensagem.encode('utf-8'))
            data = s.recv(1024).decode('utf-8').strip()
            
            # Verificar se a resposta não está vazia
            if data:
                produtos = data.split(';')
                for produto in produtos:
                    if produto:
                        nome, quantidade, preco = produto.split(',')
                        print(f"Produto: {nome}, Quantidade: {quantidade}, Preço: {preco}")
            else:
                print("Nenhum produto encontrado para a categoria especificada.")
        except Exception as e:
            print(f"Erro ao conectar-se ao produtor TCP: {e}")

# Função para comprar um produto via socket TCP
def comprar_produto_tcp(ip, porta, produto, quantidade):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, porta))
            mensagem = f"COMPRAR {produto} {quantidade}"
            s.sendall(mensagem.encode('utf-8'))
            resposta = s.recv(1024).decode('utf-8')
            print(resposta)
        except Exception as e:
            print(f"Erro ao conectar-se ao produtor TCP: {e}")

# Função principal do Marketplace
def main():
    produtores_tcp = [
        {"nome": "Produtor_TCP_1", "ip": "192.168.227.210", "porta": 65432, "tipo": "TCP"},
        {"nome": "Produtor_TCP_2", "ip": "127.0.0.1", "porta": 65433, "tipo": "TCP"},
        {"nome": "Produtor_TCP_3", "ip": "127.0.0.1", "porta": 65434, "tipo": "TCP"},
    ]

    produtores_rest = obter_produtores_rest()
    produtores = produtores_tcp + produtores_rest

    while True:
        print("\nProdutores disponíveis:")
        for idx, produtor in enumerate(produtores):
            print(f"{idx + 1}. {produtor['nome']} ({produtor['ip']}:{produtor['porta']}) - {produtor['tipo']}")

        escolha = input("Escolha um produtor pelo número (ou 'sair' para encerrar): ")
        if escolha.lower() == 'sair':
            break

        try:
            escolha = int(escolha) - 1
            produtor = produtores[escolha]
        except (ValueError, IndexError):
            print("Opção inválida.")
            continue

        while True:
            print("\n1. Listar categorias")
            print("2. Listar produtos de uma categoria")
            print("3. Comprar produto")
            print("4. Voltar")
            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                if produtor['tipo'] == 'TCP':
                    resposta = obter_categorias_tcp(produtor['ip'], produtor['porta'])
                else:
                    resposta = requests.get(f"http://{produtor['ip']}:{produtor['porta']}/categorias").json()
                if resposta:
                    print(f"Categorias: {resposta}")
            elif opcao == '2':
                categoria = input("Digite a categoria: ")
                if produtor['tipo'] == 'TCP':
                    resposta = obter_produtos_tcp(produtor['ip'], produtor['porta'], categoria)
                else:
                    resposta = requests.get(f"http://{produtor['ip']}:{produtor['porta']}/produtos", params={"categoria": categoria}).json()
                if resposta:
                    print(f"Produtos: {resposta}")
            elif opcao == '3':
                produto = input("Digite o nome do produto: ")
                quantidade = input("Digite a quantidade: ")
                if produtor['tipo'] == 'TCP':
                    resposta = comprar_produto_tcp(produtor['ip'], produtor['porta'], produto, quantidade)
                else:
                    resposta = requests.get(f"http://{produtor['ip']}:{produtor['porta']}/comprar/{produto}/{quantidade}").json()
                if resposta:
                    print(f"Resultado da compra: {resposta}")
            elif opcao == '4':
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main()

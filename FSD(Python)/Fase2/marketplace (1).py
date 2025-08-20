import requests
import socket

# Lista de configurações de produtores TCP locais
PRODUTORES_TCP = [
    {'nome': 'Produtor_TCP_1', 'ip': '127.0.0.1', 'porta': 65432, 'tipo': 'TCP'},
    {'nome': 'Produtor_TCP_2', 'ip': '127.0.0.1', 'porta': 65433, 'tipo': 'TCP'},
    {'nome': 'Produtor_TCP_3', 'ip': '127.0.0.1', 'porta': 65434, 'tipo': 'TCP'},
]

# Função para listar produtores registrados no Gestor e produtores TCP locais
def listar_produtores():
    url = "http://193.136.11.170:5001/produtor"
    resposta = requests.get(url)
    produtores = []

    # Obter produtores REST
    if resposta.status_code == 200:
        produtores_rest = resposta.json()
        if produtores_rest:
            for produtor in produtores_rest:
                # Verifica se o IP do produtor é 0.0.0.0 e substitui por 127.0.0.1 para permitir conexão local
                if produtor['ip'] == '0.0.0.0':
                    produtor['ip'] = '127.0.0.1'
                produtor['tipo'] = 'REST'
            produtores.extend(produtores_rest)
        else:
            print("Nenhum produtor REST disponível.")
    else:
        print(f"Erro ao obter lista de produtores REST: {resposta.status_code}")

    # Adicionar produtores TCP locais
    produtores.extend(PRODUTORES_TCP)

    # Exibir a lista completa de produtores
    if not produtores:
        print("Nenhum produtor disponível.")
        return []

    for idx, produtor in enumerate(produtores):
        print(f"{idx + 1}. Nome: {produtor['nome']}, IP: {produtor['ip']}, Porta: {produtor['porta']}, Tipo: {produtor['tipo']}")
    
    return produtores

# Atualizações nas funções REST para permitir a conexão com Produtor_A
def obter_categorias(ip, porta):
    url = f"http://{ip}:{porta}/categorias"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        categorias = resposta.json()
        print(f"Categorias disponíveis: {', '.join(categorias)}")
        return categorias
    else:
        print("Erro ao obter categorias.")
        return []

def obter_produtos(ip, porta, categoria):
    url = f"http://{ip}:{porta}/produtos?categoria={categoria}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        produtos = resposta.json()
        for produto in produtos:
            print(f"Produto: {produto['produto']}, Quantidade: {produto['quantidade']}, Preço: {produto['preco']}")
    elif resposta.status_code == 404:
        print("Categoria inexistente.")
    else:
        print(f"Erro ao obter produtos: {resposta.status_code}")

def comprar_produto(ip, porta, produto, quantidade):
    url = f"http://{ip}:{porta}/comprar/{produto}/{quantidade}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        print("Compra realizada com sucesso.")
    else:
        erro = resposta.json().get('erro', 'Erro desconhecido')
        print(f"Erro: {erro}")


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

# Função principal para o Marketplace se conectar a Produtores REST e realizar compras
def main():
    produtores = listar_produtores()
    if produtores:
        escolha = int(input("Escolha um produtor pelo número: ")) - 1
        produtor = produtores[escolha]
        ip = produtor['ip']
        porta = produtor['porta']
        tipo = produtor['tipo']

        while True:
            print("\n1. Listar produtos por categorias")
            print("2. Comprar produto")
            print("3. Mudar de produtor")
            print("4. Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                if tipo == 'REST':
                    categorias = obter_categorias(ip, porta)
                elif tipo == 'TCP':
                    categorias = obter_categorias_tcp(ip, porta)
                else:
                    print("Erro: Tipo de produtor desconhecido.")
                    continue

                if categorias:
                    categoria = input("Informe a categoria dos produtos: ")
                    if categoria in categorias:
                        if tipo == 'REST':
                            obter_produtos(ip, porta, categoria)
                        elif tipo == 'TCP':
                            obter_produtos_tcp(ip, porta, categoria)
                    else:
                        print("Categoria inválida.")
            elif opcao == '2':
                produto = input("Informe o nome do produto: ")
                quantidade = input("Informe a quantidade: ")

                if quantidade.isdigit() and int(quantidade) > 0:
                    if tipo == 'REST':
                        comprar_produto(ip, porta, produto, quantidade)
                    elif tipo == 'TCP':
                        comprar_produto_tcp(ip, porta, produto, quantidade)
                    else:
                        print("Erro: Tipo de produtor desconhecido.")
                else:
                    print("Erro: A quantidade deve ser um número positivo.")
            elif opcao == '3':
                print("Mudando de produtor...")
                produtores = listar_produtores()
                if produtores:
                    escolha = int(input("Escolha um novo produtor pelo número: ")) - 1
                    produtor = produtores[escolha]
                    ip = produtor['ip']
                    porta = produtor['porta']
                    tipo = produtor['tipo']
                else:
                    print("Nenhum produtor disponível para mudança.")
            elif opcao == '4':
                print("Encerrando o marketplace.")
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main()
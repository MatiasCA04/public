import socket

# Configurações dos Produtores aos quais o Marketplace vai se conectar
PRODUTORES = [
    ('127.0.0.1', 65432)  # Adicione mais produtores se necessário
]

# Categorias válidas (pode ser expandida conforme necessário)
CATEGORIAS_VALIDAS = ["fruta", "legume"]

# Função para conectar a um Produtor e solicitar lista de produtos
def listar_produtos_produtor(host, port, categorias):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        pedido = f'LISTAR {" ".join(categorias)}'
        s.sendall(pedido.encode('utf-8'))
        data = s.recv(1024)
        
        # Transformando a string de volta em um dicionário
        produtos = eval(data.decode("utf-8"))

        # Se a lista de produtos não estiver vazia, formatar a exibição
        if produtos:
            print(f'\nProdutos disponíveis de {host}:{port}:\n')
            print(f"{'Produto':<15} {'Categoria':<10} {'Quantidade':<10} {'Preço (€)':<10}")
            print("-" * 50)
            for produto, detalhes in produtos.items():
                categoria, quantidade, preco = detalhes
                print(f"{produto:<15} {categoria:<10} {quantidade:<10} {preco:<10.2f}")
            print("\n")
        else:
            print(f'\nNenhum produto disponível nas categorias selecionadas em {host}:{port}.\n')

# Função para comprar um produto de um Produtor
def comprar_produto_produtor(host, port, produto, quantidade):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        pedido = f'COMPRAR {produto} {quantidade}'
        s.sendall(pedido.encode('utf-8'))
        data = s.recv(1024)
        print(f'\nResposta do Produtor {host}:{port}: \n{data.decode("utf-8")}\n')

# Função para mostrar o menu principal
def mostrar_menu_principal():
    print("\n=========== Menu Principal ===========")
    print("1. Listar produtos")
    print("2. Comprar produtos")
    print("3. Sair")
    print("======================================\n")

# Função para listar produtos por categoria
def menu_listar_produtos():
    while True:
        categorias = input("\nDigite as categorias de produtos (separadas por espaço, ex: fruta legume): ").split()

        # Verificar se todas as categorias são válidas
        categorias_invalidas = [categoria for categoria in categorias if categoria not in CATEGORIAS_VALIDAS]
        
        if categorias_invalidas:
            print(f"\nErro: As seguintes categorias não existem: {', '.join(categorias_invalidas)}")
            print(f"Por favor, escolha entre as categorias válidas: {', '.join(CATEGORIAS_VALIDAS)}\n")
        else:
            # Se todas as categorias forem válidas, listar produtos
            for host, port in PRODUTORES:
                listar_produtos_produtor(host, port, categorias)
            break  # Sair do loop se a operação for bem-sucedida

# Função para comprar produtos
def menu_comprar_produtos():
    produto = input("\nDigite o nome do produto que deseja comprar: ")
    quantidade = int(input("Digite a quantidade a comprar: "))
    for host, port in PRODUTORES:
        comprar_produto_produtor(host, port, produto, quantidade)

# Função principal para interagir com os Produtores
def interagir_com_produtores():
    while True:
        mostrar_menu_principal()
        opcao = input("Escolha uma opção (1-3): ")

        if opcao == '1':
            menu_listar_produtos()
        elif opcao == '2':
            menu_comprar_produtos()
        elif opcao == '3':
            print("\nConexão terminada\n")
            break
        else:
            print("\nOpção inválida. Por favor, tente novamente.\n")

if __name__ == "__main__":
    interagir_com_produtores()

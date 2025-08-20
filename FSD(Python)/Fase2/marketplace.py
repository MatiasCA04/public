import requests

# Função para listar produtores registrados no Gestor
def listar_produtores():
    url = "http://193.136.11.170:5001/produtor"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        produtores = resposta.json()
        if not produtores:
            print("Nenhum produtor disponível.")
            return []
        
        for idx, produtor in enumerate(produtores):
            print(f"{idx + 1}. Nome: {produtor['nome']}, IP: {produtor['ip']}, Porta: {produtor['porta']}")
        return produtores
    else:
        print(f"Erro ao obter lista de produtores: {resposta.status_code}")
        return []

# Função para obter categorias de um Produtor REST
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

# Função para obter produtos de uma categoria de um Produtor REST
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

# Função para comprar um produto de um Produtor REST
def comprar_produto(ip, porta, produto, quantidade):
    url = f"http://{ip}:{porta}/comprar/{produto}/{quantidade}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        print("Compra realizada com sucesso.")
    else:
        erro = resposta.json().get('erro', 'Erro desconhecido')
        print(f"Erro: {erro}")

# Função principal para o Marketplace se conectar a Produtores REST e realizar compras
def main():
    produtores = listar_produtores()
    if produtores:
        escolha = int(input("Escolha um produtor pelo número: ")) - 1
        produtor = produtores[escolha]
        ip = produtor['ip']
        porta = produtor['porta']

        while True:
            print("\n1. Listar produtos por categoria")
            print("2. Comprar produto")
            print("3. Mudar de produtor")
            print("4. Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                categorias = obter_categorias(ip, porta)  # Obtenha e mostre as categorias antes de pedir a escolha
                if categorias:
                    categoria = input("Informe a categoria de produtos: ")
                    if categoria in categorias:
                        obter_produtos(ip, porta, categoria)
                    else:
                        print("Categoria inválida.")
            elif opcao == '2':
                produto = input("Informe o nome do produto: ")
                quantidade = input("Informe a quantidade: ")
                
                # Verifica se a quantidade é um número positivo
                if quantidade.isdigit() and int(quantidade) > 0:
                    comprar_produto(ip, porta, produto, quantidade)
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
                else:
                    print("Nenhum produtor disponível para mudança.")
            elif opcao == '4':
                print("Encerrando o marketplace.")
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main()
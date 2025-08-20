import socket
import threading

# Lista de configurações de produtores (diferentes IPs e portas)
PRODUTORES = [
    ('127.0.0.1', 65432),  # Produtor 1
    ('127.0.0.1', 65433),  # Produtor 2
    ('127.0.0.1', 65434),  # Produtor 3 (Adicionar mais produtores conforme necessário)
]

# Lista de produtos inicial (produto: [categoria, quantidade, preço])
produtos = {
    "maçã": ["fruta", 100, 0.5],
    "banana": ["fruta", 80, 0.3],
    "tomate": ["legume", 50, 0.7],
    "cenoura": ["legume", 60, 0.4]
}

# RLock para controle de concorrência
lock = threading.RLock()

# Função para listar produtos disponíveis por categoria
def listar_produtos(categorias):
    with lock:
        lista = {produto: detalhes for produto, detalhes in produtos.items() if detalhes[0] in categorias}
    return lista

# Função para realizar uma compra de produtos
def comprar_produto(produto, quantidade):
    with lock:
        if produto in produtos and produtos[produto][1] >= quantidade:
            produtos[produto][1] -= quantidade
            return True
        return False

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
    for host, port in PRODUTORES:
        threading.Thread(target=iniciar_produtor, args=(host, port)).start()

if __name__ == "__main__":
    iniciar_produtores()

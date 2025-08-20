import socket
import threading

# Configurações do Produtor
HOST = '127.0.0.1'  # IP do Produtor
PORT = 65433      # Porta que o Produtor vai escutar

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

# Iniciar o servidor Produtor
def iniciar_produtor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Produtor disponível em {HOST}:{PORT}')
        
        while True:
            conn, addr = server_socket.accept()
            print(f'Marketplace conectado: {addr}')
            threading.Thread(target=handle_marketplace, args=(conn,)).start()

if __name__ == "__main__":
    iniciar_produtor()

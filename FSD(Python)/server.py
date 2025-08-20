import socket

s = socket.socket()

HOST = '127.0.0.1'
PORT = 12345

s.bind(('',PORT))
print('socket binded to %s' %(PORT))

s.listen(1024)
print('socket is listening')

while True:

    c, addr = s.accept()
    print('Got connection from', addr)

    c.send('Thank you for connecting'.encode())

    c.close()

    break


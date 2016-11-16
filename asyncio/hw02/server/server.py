import asyncio
import sys
import time
from calc_md5 import md5Check
import socket

if len(sys.argv)  <2:
     print('[FilePath to write] [server_mss_size] ')
     sys.exit()
fileName =  sys.argv[1]
server_mss_size = int(sys.argv[2])

buffer_size = int(server_mss_size)
@asyncio.coroutine
def handle_echo(reader, writer):
    with open(fileName, "ab") as f:
        data = yield from reader.read(buffer_size)
        decoded_data = data.decode('utf-8')
        f.write(data)
        addr = writer.get_extra_info('peername')
#        print("Send: ok")
        writer.write("ok".encode('utf-8'))
        yield from writer.drain()
#        print("data received")
        writer.close()

def recv_client_mss_size(client_socket,addr,server_socket):
        message = client_socket.recv(4096).decode()
        print("client mss size : ",message) 
        client_mss_size = int(message)
        if client_mss_size< server_mss_size: 
             buffer_size = client_mss_size
        else:
             buffer_size = server_mss_size
        client_socket.sendto(str(buffer_size).encode(),addr)
        

ip_address = '127.0.0.1'
port_number = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip_address, port_number))
server_socket.listen(10)
client_sock, addr = server_socket.accept()
recv_client_mss_size(client_sock,addr, server_socket)


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, ip_address, "5555", loop=loop)
server = loop.run_until_complete(coro)

print('Serving on {}'.format(server.sockets[0].getsockname()))


try:
    loop.run_forever()
except KeyboardInterrupt:
    pass


# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

m  = md5Check(fileName)
print(m.check_md5())

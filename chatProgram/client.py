import sys
import socket
import threading

def recv_message(message_socket,client_ID):
	while True:
		message = message_socket.recv(4096).decode()
		sys.stdout.write('\n'+message+'\n['+client_ID+']>>')
		if message[7:11].lower() == 'quit':
			break
	print('Host Disconnected')

def send_message(my_socket,client_ID):
	while True:
		sys.stdout.write('['+client_ID+']>>')
		message = input('')
		if message[0:4].lower() == 'quit':
			break
		else:
			my_socket.send(('['+client_ID+']>>' + message).encode())
	print('Host Disconnect')
	message = '\nExit chatroom'
	my_socket.send((message+'['+client_ID+']' ).encode())
	my_socket.close()
	sys.exit()

def main():
	if len(sys.argv) !=4:
		print("python client.py [IPADDRESS] [PORTNUMBER] [CLIENT ID]")
		sys.exit()

	ip_address = sys.argv[1]
	port_number = int(sys.argv[2])
	client_ID=  sys.argv[3]

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((ip_address, port_number))

	print("Host connected")
	message = 'Enter chatroom'
	client_socket.send((message+'['+client_ID+']' ).encode())
	threading.Thread(target = recv_message, args=(client_socket,client_ID)).start()
	threading.Thread(target = send_message, args=(client_socket,client_ID)).start()


if __name__ == '__main__':
	main()

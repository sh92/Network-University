import socket
import sys
import threading
from phue_module import phue_app

server = socket.gethostbyname('irc.freenode.org')
channel = "#sanghee"
arg_lens =  len(sys.argv)
botnick = "H201202160"
phue_bridge_ip = '192.168.0.16'
#str(sys.argv[1])

def recv_message(message_socket,client_ID):
    while True:
        message = message_socket.recv(4096).decode()
        sys.stdout.write(message)
        if message[8:11].lower() == 'quit':
            break
    print('Host Disconnected')

def send_message(my_socket,client_ID):
    while True:
        message = input('')
        if message[0:4].lower() == 'quit':
            break
        else:
            message = 'PRIVMSG '+channel+' : '+message+"\r\n"
            my_socket.send(message.encode())
    print('Host Disconnect')
    message = '\nExit chatroom'
    my_socket.send(message.encode())
    my_socket.close()
    sys.exit()



irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
print("connecting to:"+server)
irc.connect((server, 6667))                                                        

user = "USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun bot!\n"
irc.send(user.encode())

nick = "NICK "+ botnick +"\n"
irc.send(nick.encode())

priv= "PRIVMSG nickserv :iNOOPE\r\n"
irc.send(priv.encode())

join = "JOIN "+ channel +"\n"
irc.send(join.encode())


threading.Thread(target = recv_message, args=(irc,botnick)).start()
threading.Thread(target = send_message, args=(irc,botnick)).start()

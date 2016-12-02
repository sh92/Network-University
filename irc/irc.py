import socket
import sys
import threading
from phue_module import phue_app
import time

botnick = "H201202160"
server = socket.gethostbyname('irc.freenode.org')
channel = "#SHSHSH"
arg_lens =  len(sys.argv)
phue_bridge_ip = '192.168.0.16'

def recv_message(message_socket,client_ID):
    while True:
        message = message_socket.recv(4096).decode()
        sys.stdout.write(message)
	p = phue_app(phue_bridge_ip)
	index = message.rindex(':')
	command = str(message[index+1:])
	clist = command.split()
	password= str(clist[0])
	if password != 'H201202160':
		continue
	num= int(clist[1])
	option = clist[2]
	if option == 'O':
		on_off= int(clist[3])
		p.on_off(num,on_off)
	elif option == 'B':
		bright = int(clist[3])
		p.bright_change(num,bright)
	elif option == 'C':
		x = float(clist[3])
		y = float(clist[4])
		p.color_change(num,x,y)
	phue_msg = 'PRIVMSG '+channel+" : "
	phue_msg +=p.showPhue()
	phue_msg +="\r\n"
	message_socket.send(phue_msg.encode())
	
	
        if message[8:11].lower() == 'quit':
            break

def send_message(my_socket,client_ID):
    while True:
        message =raw_input('')
        if message[0:4].lower() == 'quit':
            break
        else:
            message = 'PRIVMSG '+channel+' : '+message+"\r\n"
            my_socket.send(message.encode())
    my_socket.close()
    sys.exit()



irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
irc.connect((server, 6667))                                                        

user = "USER "+ botnick +" "+ botnick +" "+ botnick +" :This is a fun bot!\n"
irc.send(user.encode())

nick = "NICK "+ botnick +"\n"
irc.send(nick.encode())

priv= "PRIVMSG nickserv :iNOOPE\r\n"
irc.send(priv.encode())

join = "JOIN "+ channel +"\n"
irc.send(join.encode())

time.sleep(2)
threading.Thread(target = recv_message, args=(irc,botnick)).start()
threading.Thread(target = send_message, args=(irc,botnick)).start()

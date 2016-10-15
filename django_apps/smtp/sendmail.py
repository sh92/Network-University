from socket import *
import base64

class mail:
    params =None
    user = None
    password = None
    mail_to =None
    mail_from = None
    subject = None
    body = None

    def __init__(self,params):
        self.params = params
        self.user=params.get('ID')
        self.password = params.get('PASSWORD')
        self.mail_to =params.get('EMAIL_TO')
        self.subject = params.get('SUBJECT')
        self.body = params.get('BODY')


    def replySeverMessage(self,clientSocket , sentence):
        clientSocket.send(sentence)
        serverSentence = clientSocket.recv(1024)
        print('S :', serverSentence)
        print("\n")

    def send_mail(self):
        if self.params is None:
            return None
        serverName ='cuvic.cnu.ac.kr'
        serverPort = 25
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName,serverPort))

            user = self.user
            password = self.password
            mail_to = self.mail_to
            subject = self.subject
            body = self.body


            host_name = 'cnu.ac.kr'
            mail_from = user + '@' + host_name

            sentence = b'EHLO '+mail_from.encode()+b'\r\n'
            print("C : EHLO "+mail_from+'\r\n')
            self.replySeverMessage(clientSocket,sentence)

            sentence = b'AUTH LOGIN\r\n'
            print("C : AUTH LOGIN\r\n")
            self.replySeverMessage(clientSocket,sentence)


            sentence = base64.b64encode(user.encode())+b"\r\n"
            self.replySeverMessage(clientSocket, sentence)


            sentence = base64.b64encode(password.encode())+b"\r\n"
            self.replySeverMessage(clientSocket, sentence)

            sentence = b"MAIL FROM: " + mail_from.encode()+b"\r\n"
            print("C : MAIL FROM: "+mail_from+'\r\n')
            self.replySeverMessage(clientSocket, sentence)

            sentence = b"RCPT TO: " + mail_to.encode()+b"\r\n"
            print("C : RCPT TO: "+mail_to+'\r\n')
            self.replySeverMessage(clientSocket, sentence)

            sentence = b"DATA\r\n"
            print("C : DATA:\r\n")
            self.replySeverMessage(clientSocket, sentence)

            sentence = b"SUBJECT: "+ subject.encode() + b"\r\n"
            print("C : SUBJECT: "+subject+"\r\n\n")
            clientSocket.send(sentence)

            sentence = b"FROM: " + mail_from.encode() + b"\r\n"
            print("C : FROM: "+mail_from+"\r\n\n")
            clientSocket.send(sentence)

            sentence = b"TO: " + mail_to.encode() +b"\r\n"
            print("C : TO: "+mail_to+"\r\n\n")
            clientSocket.send(sentence)

            print("Send e-mail from "+mail_from+" to "+ mail_to+"\r\n")

            sentence = body.encode()+b"\r\n"
            self.replySeverMessage(clientSocket, sentence)

            sentence = b".\r\n"
            print("C : .\r\n")
            self.replySeverMessage(clientSocket, sentence)

            sentence = b"QUIT\r\n"
            print("C : QUIT\r\n")
            self.replySeverMessage(clientSocket, sentence)

            clientSocket.close()
            return "SUCCESS"
        except socket.error as e:
            if 'Connection refused' in e:
                print('*** Connection refused ***')
            else:
                print(e)
            return None

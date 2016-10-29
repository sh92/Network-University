import socket
import time

UDP_IP = ""
UDP_PORT = 5005
buffer_size = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))


print "ready for client ... "

try:
    R=0
    
    temp = (R+1)%2
    ACK = "ACK"+str(temp)
    NAK = "NAK"+str(temp)
    #fileName
    while True:
        try:
            fileName, addr = sock.recvfrom(buffer_size)
            if fileName[-1] == str(R):
                break;
            else:
                sock.sendto(NAK, addr)
                print "NAK",temp
        except socket.timeout:
            print "retransmit NAK packet"
            sock.sendto(NAK, addr)

    while True:
        try:
            sock.sendto(ACK, addr)
            print "ACK",temp
            break;
        except socket.timeout:
            print "retransmit ACK packet"
        
    R = (R+1)%2
    fileName = fileName[:-1]
    print "File Name: ", fileName

    
    #filesize
    temp=(R+1)%2
    ACK="ACK"+str(temp)
    NAK="NAK"+str(temp)
    while True:
        try:
            filesize, addr = sock.recvfrom(buffer_size)
            if filesize[-1] == str(R):
                break;
            else:
                sock.sendto(NAK, addr)
                print "NAK",temp
        except socket.timeout:
            print "retransmit NAK"
            sock.sendto(NAK, addr)

    while True:
        try:
            sock.sendto(ACK,addr)
            print "ACK",temp
            break;
        except:
            print "retransmit ACK"

    R = (R+1)%2
    filesize = filesize[:-1]
    print "File Size: ", filesize

    size = 0
    remain= int(filesize)

    start_time = time.time()
    while True:
        with open(fileName, "ab") as f:
            if remain >= buffer_size:
                temp = (R+1) % 2
                ACK = "ACK"+str(temp)
                NAK = "NAK"+str(temp)

                while True:
                    fileInfo , addr = sock.recvfrom(buffer_size+1)
                    #time.sleep(1)
                    try:
                        if fileInfo[-1] == str(R):
                            break;
                        else:
                            sock.sendto(NAK, addr)
                            print "NAK",temp
                    except socket.timeout:
                        print "timeout retransmit NAK",temp
                        sock.sendto(NAK, addr)

                while True:
                    try:
                        sock.sendto(ACK, addr)
                        print "ACK",temp
                        break;
                    except socket.timeout:
                        print "timeout retransmit ACK",temp


                R = (R+1)%2
                fileInfo = fileInfo[:-1]
                f.write(fileInfo)
                remain -=buffer_size
                size += buffer_size
                print size ,"/", filesize ," (currentsize/totalsize) ,", round((100.00 *size/int(filesize)),2) ,"%"


            else:
                temp = (R+1) %2
                ACK = "ACK"+str(temp)
                NAK = "NAK"+str(temp)
                while True:
                    try:
                        fileInfo , addr = sock.recvfrom(remain+1)
                        if fileInfo[-1] == str(R):
                            break;
                        else:
                            sock.sendto(NAK, addr)
                            print "NAK",temp
                    except socket.timeout:
                        print "timeout retansmit NAK",temp
                        sock.sendto(NAK, addr)

                while True:
                    try:
                        sock.sendto(ACK, addr)
                        print "ACK",temp
                        break;
                    except socket.timeout:
                        print "timeout retansmit ACK",temp

                
                R = (R+1)%2
                fileInfo = fileInfo[:-1]
                f.write(fileInfo)
                size+=remain
                print size ,"/", filesize ," (currentsize/totalsize) ,", round((100.00 *size/int(filesize)),2) ,"%"
                print "Completed ...."
                break

    end_time = time.time()
    print "Time elapsed : ", end_time - start_time
        
except socket.error as e:
    print e
    sys.exit()

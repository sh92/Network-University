import socket
import time

UDP_IP = ""
UDP_PORT = 5005
buffer_size = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))

print "ready for client ... "

try:

    fileName, addr = sock.recvfrom(buffer_size)
    print "File Name: ", fileName

    filesize, addr = sock.recvfrom(buffer_size)
    print "File Size: ", filesize
    size = 0
    remain= int(filesize)

    start_time = time.time()
    while True:
        with open(fileName, "ab") as f:
            if remain >= buffer_size:
                fileInfo , addr = sock.recvfrom(buffer_size)
                f.write(fileInfo)
                remain -=buffer_size
                size += buffer_size
                print size ,"/", filesize ," (currentsize/totalsize) ,", round((100.00 *size/int(filesize)),2) ,"%"

            else:
                fileInfo , addr = sock.recvfrom(remain)
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

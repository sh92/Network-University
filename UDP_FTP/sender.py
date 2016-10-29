import os
import socket
import sys
import time

ServerIP = sys.argv[1] 
ServerPORT = int(sys.argv[2])
filePath = sys.argv[3]
buffer_size =1024

if len(sys.argv)  < 3:
  print '[Dest IP Addr] [Dest Port] [File Path]'
  sys.exit()
try:
  sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
  sock.settimeout(1)
  size=0
  filesize = os.path.getsize(filePath) 
  remain = filesize


  print "FileName : ", filePath
  sock.sendto(filePath,(ServerIP, ServerPORT))
  time.sleep(1/20.0)

  print "FileSize : ", filesize
  sock.sendto(str(filesize),(ServerIP, ServerPORT))
  time.sleep(1/20.0)

  start_time = time.time()
  with open(filePath, 'rb') as f:
    while True:
      if remain >= buffer_size:
        remain -=buffer_size
        read_data = f.read(buffer_size)
        size += buffer_size
        print size , "/",filesize , "(Currentsize/Totalsize) , ", round((100.00 * size/int(filesize)),2), "%"
        sock.sendto(read_data,(ServerIP, ServerPORT))
        time.sleep(1/20.0)

      else:
        size+=remain
        read_data = f.read(remain)
        print size , "/",filesize , "(Currentsize/Totalsize) , ", round((100.00 * size/int(filesize)),2), "%"
        sock.sendto(read_data,(ServerIP, ServerPORT))
        time.sleep(1/20.0)

        print "Completed ..."
        break

    end_time = time.time()
    print "Time elapsed : ", end_time - start_time

except socket.error as e:
  print e
  sys.exit()

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
  S=0
  ackSize=4

  #filePath
  myFrame = filePath+str(S)

  nxt = (S+1)%2
  while True:
    try:
      print "seqNo:",S
      sock.sendto(myFrame,(ServerIP, ServerPORT))
      ACK, addr = sock.recvfrom(ackSize);
      if ACK == 'ACK'+str(nxt):
        print "ACK receive",nxt
        break;
      elif ACK == "NAK"+str(nxt):
        print "NAK receive",nxt
    except socket.timeout:
      print "time out, retransmit! seq No:",S

  print "FileName : ", filePath


  #filesize
  S=(S+1)%2
  myFrame = str(filesize)+str(S)

  nxt= (S+1)%2
  while True:
    try:
      print "seqNo:",S
      sock.sendto(myFrame,(ServerIP, ServerPORT))
      ACK, addr = sock.recvfrom(ackSize);
      if ACK == 'ACK'+str(nxt):
        print "ACK receive ",nxt
        break;
      elif ACK=="NAK"+str(nxt):
        print "NAK receive ",nxt
    except socket.timeout:
      print "time out, retransmit! seq No:",S

  print "FileSize : ", filesize

  start_time = time.time()
  with open(filePath, 'rb') as f:
    while True:
      if remain >= buffer_size:
        remain -=buffer_size
        read_data = f.read(buffer_size)
        size += buffer_size
        S = (S+1)%2
        myFrame = read_data+str(S)
        nxt = (S+1)%2
        while True:
          try : 
            #time.sleep(1)
            print "seqNo",S
            sock.sendto(myFrame,(ServerIP, ServerPORT))
            ACK, addr = sock.recvfrom(ackSize)
            if ACK == 'ACK'+str(nxt):
              print "ACK receive",nxt
              break;
            elif ACK == 'NAK'+str(nxt):
              print "NAK receive",nxt
          except socket.timeout:
            print "time out, retransmit! seq no:", S
        print size , "/",filesize , "(Currentsize/Totalsize) , ", round((100.00 * size/int(filesize)),2), "%"
      else:
        size+=remain
        read_data = f.read(remain)
        S = (S+1)%2
        myFrame = read_data+str(S)
        nxt = (S+1)%2
        while True:
          try:
            print "seqNo",S
            sock.sendto(myFrame,(ServerIP, ServerPORT))
            ACK, addr = sock.recvfrom(ackSize);
            if ACK == 'ACK'+str(nxt):
              print "ACK receive ",nxt
              break;
            elif ACK == 'NAK'+str(nxt):
              print "NAK receive",nxt
          except socket.timeout:
            print "time out, retransmit!"
            print "seq no:",S 

        print size , "/",filesize , "(Currentsize/Totalsize) , ", round((100.00 * size/int(filesize)),2), "%"
        print "Completed ..."
        break

    end_time = time.time()
    print "Time elapsed : ", end_time - start_time

except socket.error as e:
  print e
  sys.exit()

import os
import socket
import sys
import time

ServerIP = sys.argv[1] 
ServerPORT = int(sys.argv[2])
filePath = sys.argv[3]
buffer_size =1460

def getChecksum(data):
  sum=0
  for i in range(0, len(data), 2):
    if i+1 < len(data):
      data16= ord(data[i]) + (ord(data[i+1]) << 8) 
      tempSum = sum + data16 
      sum = (tempSum & 0xffff) + (tempSum >> 16)    
  return ~sum & 0xffff

def computeWindow(size):
  temp =1
  while temp<size:
    temp *=2
  if temp ==1:
    return 1
  else:
    return temp/2

if len(sys.argv)  < 3:
  print '[Dest IP Addr] [Dest Port] [File Path]'
  sys.exit()
try:
  sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
  sock.settimeout(0.1)
  size=0
  filesize = os.path.getsize(filePath) 
  totalFrame= filesize / buffer_size
  seqsize = totalFrame
  if seqsize > 256: 
    seqsize = 256 
  maximumSeqSize = int('0xffffffff',16)
  if maximumSeqSize < totalFrame:
    print "File Size should be less than " , maximumSeqSize * buffer_size, " Byte"
    raise Exception("OverSizeException")
     
  windowsize  = computeWindow(seqsize)


  print "window size is ",windowsize
  print "seq size is ",seqsize
  print "total Frame number is ", totalFrame

  wfrom=0
  wto = wfrom + windowsize

  S=0
  ackSize=4

  #filePath
  myFrame = filePath+str(S)

  nxt = (S+1)%2
  while True:
    try:
      sock.sendto(myFrame,(ServerIP, ServerPORT))
      ACK, addr = sock.recvfrom(ackSize);
      if ACK == 'ACK'+str(nxt):
        print "ACK receive",nxt
        break;
      elif ACK == "NAK"+str(nxt):
        print "NAK receive",nxt
    except socket.timeout:
      print "time out, resend! seq No:",S

  print "FileName : ", filePath


  #filesize
  S=(S+1)%2
  myFrame = str(filesize)+str(S)

  nxt= (S+1)%2
  while True:
    try:
      sock.sendto(myFrame,(ServerIP, ServerPORT))
      ACK, addr = sock.recvfrom(ackSize);
      if ACK == 'ACK'+str(nxt):
        print "ACK receive ",nxt
        break;
      elif ACK=="NAK"+str(nxt):
        print "NAK receive ",nxt
    except socket.timeout:
      print "time out, resend! seq No:",S

  print "FileSize : ", filesize
  print "================up is stop and wait ARQ============================"
  print "================down is selective ARQ==============================="

  start_time = time.time()
  Buffer=  {}
  Rremain=filesize
  remain= filesize% buffer_size
  Rsize = size
  isSend = {}
  isACK = {}
  isSend = isSend.fromkeys(range(totalFrame+2),[])
  isACK= isACK.fromkeys(range(totalFrame+2),[])
  ackSeqSize = 8
  charSize = 3
  for i in range(totalFrame+2):
    isSend[i].append(0)
    isACK[i].append(0)

  with open(filePath, 'rb') as f:
    while True:
      if Rremain == 0:
        break
      #### Send Frame ####
      for i in range(wfrom,wto):
        if i >= totalFrame+1:
          continue
        if isACK[i+1]==1:
          continue
        if isSend[i] == 1 :
          continue
        frame_size = buffer_size

        read_data = f.read(frame_size)

        seq='{0:08x}'.format(i)
        
        checksum=getChecksum(read_data)
        checksumSeq =  "{0:04x}".format(checksum)
        
        checksumInt =  int (checksumSeq,16)
        Buffer[i%seqsize] = read_data+str(seq)+checksumSeq

      for i in range(wfrom, wto):
      #for i in range(wto-1,wfrom-1,-1):   # reverse
        if i >= totalFrame+1:
          continue
        if isACK[i+1]==1:
          continue
        if isSend[i] == 1 :
          continue
        #time.sleep(1)
        print "send seqNo",i %seqsize
        sock.sendto(Buffer[i % seqsize],(ServerIP,ServerPORT))
        isSend[i] =1

      
      #### Receive Reply ####
      start = wfrom
      end=wto
      print "window start : ",start
      print "window end :  " , end-1

      try :
        ACK,addr = sock.recvfrom(charSize+ackSeqSize)
        frameSeq = ACK[charSize:]
        frameNo = int(frameSeq,16)
        print "frameNo: " , frameNo
        print "seqNo: " , frameNo %seqsize
        if frameNo in range(start,end+1):
          ### ACK ####
          if ACK == 'ACK'+str(frameSeq):
            if isACK[frameNo] ==1 :
              continue 
            print "ACK receive", frameNo %seqsize
            if frameNo == totalFrame+1:
              Rremain -= remain
              Rsize += remain
            else:
              Rremain-=buffer_size
              Rsize += buffer_size

            print Rsize , "/",filesize , "(Currentsize/Totalsize) , ", round((100.00 * Rsize/int(filesize)),2), "%"

            isACK[frameNo] =1
            #window move
            if frameNo==wfrom+1:
              n=frameNo
              while True:
                if n >=totalFrame+1:
                  break
                if isACK[n] == 1:
                  wfrom+=1
                  wto+=1
                  n+=1
                else:
                  break

          ### NAK ###
          elif ACK == "NAK"+str(frameSeq): 
            if isACK[frameNo+1] ==1:
              continue
            print "NAK receive", frameNo %seqsize
            print "resend!",frameNo %seqsize
            sock.sendto(Buffer[frameNo%seqsize],(ServerIP,ServerPORT))
      ### time out ###
      except socket.timeout:
        for i in range (start, end):
          if i>= totalFrame+1:
            break 
          if isACK[i+1] ==1:
            continue
          if isSend[i] ==1:
            print "Timeout , resend! from seqNo",i%seqsize
            sock.sendto(Buffer[i%seqsize],(ServerIP,ServerPORT))
            continue

    print "Completed ..."
    end_time = time.time()
    print "Time elapsed : ", end_time - start_time
except Exception as error:
  print('caught this error: ' + repr(error))
except socket.error as e:
  print e
  sys.exit()

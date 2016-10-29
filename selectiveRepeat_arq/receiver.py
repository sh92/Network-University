import socket
import time

UDP_IP = ""
UDP_PORT = 5005
buffer_size = 1460

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))


print "ready for client ... "
def verifyChecksum(data, checksum):
    sum = 0
    for i in range(0, len(data), 2):
        if i+1 < len(data):
            data16= ord(data[i]) + (ord(data[i+1]) << 8)      
            tempSum= sum +data16
            sum = (tempSum & 0xffff) + (tempSum >> 16)      
    currChk = sum & 0xffff 
    result = currChk & checksum
    if result == 0:
        return True
    else:
        return False

def computeWindow(size):
    temp =1
    while temp < size:
        temp *=2
        
    if temp == 1:
        return 1
    else:
        return temp/2

try:
    R=0
    temp = (R+1) % 2
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
        
    R = (R+1) %2
    fileName = fileName[:-1]
    print "File Name: ", fileName

    
    #filesize
    temp=(R+1) %2
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

    filesize = filesize[:-1]
    print "File Size: ", filesize

    size = 0
    remain= int(filesize)



    # window size ande seq size
    totalFrame= remain/ buffer_size
    seqsize = totalFrame
    if seqsize > 256:
        seqsize = 256
    maximumSeqSize=int('0xffffffff',16)
    if maximumSeqSize < totalFrame:
        print "File Size should be less than " , maximumSeqSize * buffer_size, " Byte"
        raise Exception("OverSizeException")
    windowsize = computeWindow(seqsize)



    print "window size is ", windowsize
    print "seqsize is ", seqsize
    wfrom = 0
    wto = wfrom + windowsize



    print "===========up is  stop and ARQ=========="
    print "===========down is selective ARQ======"

    start_time = time.time()
    Buffer={}
    isACK = {}
    isACK = isACK.fromkeys(range(totalFrame+2),[])
    ackSeqSize = 8 
    checksumSize = 4
    lastframe = int(filesize) % buffer_size
    for i in range(totalFrame+2):
        isACK[i].append(0)

    initTrue=True
    while True:
        with open(fileName, "ab") as f:
            if remain== 0:
                for i in range(wfrom,totalFrame+1):
                    f.write(Buffer[i%seqsize])
                print "Completed ...."
                break
                
            framesize = buffer_size
            fileInfo , addr = sock.recvfrom(framesize+ackSeqSize+checksumSize)
            checksumSeq =  fileInfo[-checksumSize:]
            checksum = int(checksumSeq ,16)

            frameSeq = fileInfo[-(ackSeqSize+checksumSize) : -checksumSize]
            frameNo = int(frameSeq,16)
        
            fileData=fileInfo[:-(ackSeqSize+checksumSize)]
            # checksum Test
            #if frameNo == 2 and initTrue:
            #    fileData = str(111111111111)
            #    initTrue=False
            ackNo= frameNo+1
            ackSeq ='{0:08x}'.format(ackNo)

            if verifyChecksum(fileData,checksum) == False:
                print "Checksum is False"
                print "NAK",frameNo
                sock.sendto("NAK"+str(frameSeq), addr)
                continue


            print "frameNo:" ,frameNo
            print "seqNo:" ,frameNo %seqsize
            print "window start : ",wfrom
            print "window end : ", wto -1
            
            if frameNo in range(wfrom,wto):
                if frameNo >= totalFrame+1:
                    continue 
                if isACK[frameNo] !=1:
                    if frameNo == totalFrame:
                        size += lastframe
                        remain -= lastframe
                    else:    
                        size += framesize
                        remain -= framesize
                    print size ,"/", filesize ," (currentsize/totalsize) ,", round((100.00 *size/int(filesize)),2) ,"%"
                #time.sleep(1)
                Buffer[frameNo%seqsize] =fileData
                isACK[frameNo]=1
                if frameNo==wfrom:
                    n=frameNo
                    while True:
                        if n >= totalFrame+1:
                            break
                        if isACK[n] == 1:
                            f.write(Buffer[n % seqsize])
                            wfrom+=1
                            wto+=1
                            n+=1
                        else:
                            break
                sock.sendto("ACK"+str(ackSeq), addr)
                print "send ACK",str(ackNo%seqsize) 
            else:
                if isACK[frameNo] == 1:
                    sock.sendto("ACK"+str(ackSeq), addr)
                    continue
                print "NAK",frameNo%seqsize
                sock.sendto("NAK"+str(frameSeq), addr)


    end_time = time.time()
    print "Time elapsed : ", end_time - start_time
except Exception as error:
    print('caught this error: ' + repr(error))
except socket.error as e:
    print e
    sys.exit()

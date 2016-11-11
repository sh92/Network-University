import socket, sys
from struct import *
import hashlib
import os
import time

buffer_size = 1460
filePath = sys.argv[1]
'''
dest_ip = sys.argv[1]
dest_port = int(sys.argv[2])
filePath = sys.argv[3]

if len(sys.argv) < 3:
	print '[Dest IP Addr] [Dest Port] [File Path]'
	sys.exit()
'''

def check_md5(file_path, block_size=1460):
    md5 = hashlib.md5()
    try:
        f=open(file_path,'rb')
    except IOError as e:
	print(e)
        return
    while True:
        buf =  f.read(block_size)
        if not buf:
            break
        md5.update(buf)
	#print(md5.hexdigest())
	#md5.update(data)
    return  md5.hexdigest()

def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg)-1, 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s


def getChecksum(data):
  sum=0
  for i in range(0, len(data), 2):
    if i+1 < len(data):
      data16= ord(data[i]) + (ord(data[i+1]) << 8) 
      tempSum = sum + data16 
      sum = (tempSum & 0xffff) + (tempSum >> 16)    
  return ~sum & 0xffff
   

#ip header
def ip_packet(src_ip,dest_ip):
	ip_ihl = 5
	ip_ver = 4
	ip_tos = 0 
	ip_tot_len = 0
	ip_packet_id = 12345
	ip_frag_off = 0
	ip_ttl = 255
	ip_proto = socket.IPPROTO_TCP
	ip_checksum = 0
	ip_saddr = socket.inet_aton(src_ip)
	ip_daddr = socket.inet_aton(dest_ip)
	ip_ihl_ver = (ip_ver<<4 ) +ip_ihl
	return pack('!BBHHHBBH4s4s',ip_ihl_ver, ip_ihl,ip_tos, ip_packet_id, ip_frag_off,ip_ttl, ip_proto,ip_checksum,ip_saddr,ip_daddr)

def make_tcp_checksum(src_ip,dest_ip,tmp_hdr,data):
        src_addr = socket.inet_aton(src_ip)
        dest_addr = socket.inet_aton(dest_ip)
        placeholder=0
        protocol = socket.IPPROTO_TCP
        tcp_len = len(tmp_hdr) + len(data)

        pseudo_hdr= pack('!4s4sBBH', src_addr, dest_addr , placeholder, protocol, tcp_len)
        tmp = pseudo_hdr + tmp_hdr +data
        tcp_checksum= getChecksum(tmp)
        #tcp_checksum= checksum(tmp)
	return tcp_checksum

def tcp_packet(seqNo,src_port,dest_port,src_ip,dest_addr,data,falgs):

        tcp_src_port = src_port
        tcp_dest_port = dest_port
        tcp_seq = seqNo
        tcp_ack_seq = seqNo+len(data)
        tcp_offset = 5
        fin = flags['fin']
        syn = flags['syn']
        rst = flags['rst']
        psh = flags['psh']
        ack = flags['ack']
        urg = flags['urg']
        tcp_window  = socket.htons(5840)
        tcp_checksum=0
        tcp_urg_ptr = 0

        tcp_offset_real = (tcp_offset << 4 ) + 0 
        tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)

        tmp_hdr = pack('!HHLLBBHHH' , tcp_src_port,tcp_dest_port,tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags, tcp_window, tcp_checksum, tcp_urg_ptr)
	tcp_checksum = make_tcp_checksum(src_ip,dest_ip,tmp_hdr,data)

        tcp_header = pack('!HHLLBBH' , tcp_src_port, tcp_dest_port, tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags,  tcp_window) +pack('H' , tcp_checksum) + pack('!H' , tcp_urg_ptr)
	return tcp_header


def make_packet(src_ip,dest_ip,src_port,dest_port,seqNo,data,ip_packet,flags):
    tcp_header = tcp_packet(seqNo, src_port,dest_port,src_ip,dest_ip, data,flags)
    return ip_header + tcp_header + data


try:
    sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    #s.settimeout(0.1)
    #filesize = os.path.getsize(filePath)
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()



packet = ' '
src_ip = '127.0.0.1'
dest_ip = '127.0.0.1'
src_port = 1234
dest_port = 80
ip_header = ip_packet(src_ip,dest_ip)


filesize = os.path.getsize(filePath) 
DataSize= filesize
maximumSeqSize = int('0xffffffff',16)
if maximumSeqSize < DataSize:
    print "File Size should be less than " , maximumSeqSize , " Byte"
    raise Exception("OverSizeException")
print "Data is ", DataSize

seqNo=0

#filePath
data = filePath
print data
flags  = {'fin':0,'syn':1,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(src_ip,dest_ip,src_port,dest_port,data,seqNo,ip_packet,flags)


while True:
    try:
        sock.sendto(packet,(dest_ip, 0))
        Reply= sock.recvfrom(buffer_size);
	print Reply
        if Reply == 'ACK'+str(seqNo+1):
            print "ACK receive",seqNo
            break
        elif Reply== "NAK"+str(seqNo):
            print "NAK receive",seqNo
    except socket.timeout:
        print "time out, resend! seq No:",seqNo

print "FileName : ", filePath

nextSeqNo = seqNo + len(data)
seqNo = nextSeqNo
print seqNo+"@"
#filesize
data = str(filesize)
nextSeqNo=  seqNo +len(data)
tcp_header = tcp_packet(seqNo, src_port,dest_port,src_ip,dest_ip, data)
packet = ip_header + tcp_header + data
sock.sendto(packet,(dest_ip, dest_port))
while True:
    try:
        sock.sendto(packet,(dest_ip, dest_port))
        Reply= sock.recvfrom(buffer_size);
        if Reply == 'ACK'+str(seqNo+1):
            print "ACK receive ",seqNo
            break;
        elif Reply =="NAK"+str(seqNo):
            print "NAK receive ",seqNo
    except socket.timeout:
      print "time out, resend! seq No:",seqNo

print "FileSize : ", filesize

'''


start_time = time.time()
Buffer=  {}
Rremain=filesize
remain= filesize% buffer_size
Rsize = size
isSend = {}
isACK = {}
isSend = isSend.fromkeys(range(DataSize+2),[])
isACK= isACK.fromkeys(range(DataSize+2),[])
ackSeqSize = 8
charSize = 3
for i in range(DataSize+2):
    isSend[i].append(0)
    isACK[i].append(0)
'''

'''
with open(filePath, 'rb') as f:
    start_time = time.time()
    while True:
        if Remain ==0:
            break
	#### Send Frame ####
        for i in range(wfrom,wto):
            if i >= DataSize+1:
                continue
            if isACK[i+1]==1:
                continue
            if isSend[i] == 1 :
                continue
            frame_size = buffer_size
            read_data = f.read(frame_size)
            seq='{0:08x}'.format(i)
            checksum=check_md5(read_data)
            checksumSeq =  "{0:04x}".format(checksum)
            checksumInt =  int (checksumSeq,16)
            Buffer[i%DataSize] = read_data+str(seq)+checksumSeq
         for i in range(wfrom, wto):
            #for i in range(wto-1,wfrom-1,-1):   # reverse
            if i >= DataSize+1:
                 continue
            if isACK[i+1]==1:
                 continue
            if isSend[i] == 1 :
                 continue
                #time.sleep(1)
            print "send seqNo",i %DataSize
            sock.sendto(Buffer[i % DataSize],(dest_ip,dest_port))
            isSend[i] =1

	    packet = tcp_packet(seq,data)
            s.sendto(packet, (dest_ip, 0))
        

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
            print "seqNo: " , frameNo %DataSize
            if frameNo in range(start,end+1):
            ### ACK ####
            if ACK == 'ACK'+str(frameSeq):
                if isACK[frameNo] ==1 :
                    continue 
            print "ACK receive", frameNo %DataSize
            if frameNo == DataSize+1:
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
                    if n >=DataSize+1:
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
            print "NAK receive", frameNo %DataSize
            print "resend!",frameNo %DataSize
            sock.sendto(Buffer[frameNo%DataSize],(dest_ip,dest_port))
      ### time out ###
        except socket.timeout:
            for i in range (start, end):
                if i>= DataSize+1:
                    break 
                if isACK[i+1] ==1:
                    continue
                if isSend[i] ==1:
                    print "Timeout , resend! from seqNo",i%DataSize
                    sock.sendto(Buffer[i%DataSize],(dest_ip,dest_port))
                    continue

    print "Completed ..."
    end_time = time.time()
    print "Time elapsed : ", end_time - start_time
except Exception as error:
  print('caught this error: ' + repr(error))
except socket.error as e:
  print e
  sys.exit()

'''

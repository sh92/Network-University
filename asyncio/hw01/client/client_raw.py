import socket, sys
from struct import *
import hashlib
import os
import time
import threading

buffer_size = 1460
client_mss_size =  1460
server_mss_size = 0
default_hdr_size = 40

filePath = sys.argv[1]
'''
dest_ip = sys.argv[1]
dest_port = int(sys.argv[2])
filePath = sys.argv[3]

if len(sys.argv) < 3:
	print '[Dest IP Addr] [Dest Port] [File Path]'
	sys.exit()
'''
local_ip = socket.gethostbyname(socket.gethostname())
src_ip = '127.0.0.1'
dest_ip = '127.0.0.1'
src_port = 6000
dest_port = 5000

def unPack_header(packet):
    ip_dict = unPackIP_header(packet)
    tcp_dict = unPackTCP_header(packet,ip_dict['iph_length'])
    return ip_dict, tcp_dict

def unPackIP_header(packet):
    packet= packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    ttl = iph[5]
    protocol = iph[6]
    src_ip= socket.inet_ntoa(iph[8]);
    dest_ip= socket.inet_ntoa(iph[9]);
    ip_dict = {'iph_length':iph_length,'version':version,'ttl':ttl,'protocol':protocol,'src_ip':src_ip,'dest_ip':dest_ip}
    return ip_dict

def getFlagDict(flags):
    cwr = (flags & 0x80) >> 7
    ece = (flags & 0x40) >> 6
    urg = (flags & 0x20) >> 5
    ack = (flags & 0x10) >> 4
    psh = (flags & 0x8) >> 3
    rst = (flags & 0x4) >> 2
    syn = (flags & 0x2) >> 1
    fin = (flags & 0x1) 
    flag_dict = {'cwr':cwr,'ece':ece,'urg':urg,'ack':ack,'psh':psh,'rst':rst,'syn':syn,'fin':fin}
    return flag_dict

def unPackTCP_header(packet,iph_length):
    packet= packet[0]
    tcp_header = packet[iph_length:iph_length+20]
    tcp_hdr = unpack('!HHLLBBHHH' , tcp_header)
     
    src_port = tcp_hdr[0]
    dest_port = tcp_hdr[1]
    sequence = tcp_hdr[2]
    acknowledgement = tcp_hdr[3]
    doff_reserved = tcp_hdr[4]
    tcp_hdr_length = doff_reserved >> 4
    flags = tcp_hdr[5]

    h_size = iph_length + tcp_hdr_length * 4
    data_size = len(packet) - h_size
    mss=0
    if tcp_hdr_length > 5: 
        option_pack = packet[iph_length + 20: h_size] 
        option_hdr = unpack('!BBH',option_pack)
        option_type = option_hdr[0]
        if option_type == 2:
            mss = option_hdr[2]
     
    #get data from the packet
    data = packet[h_size:]
    tcp_dict = {'src_port':src_port,'dest_port':dest_port,'sequence':sequence,'acknowledgement':acknowledgement,'tcp_hdr_length':tcp_hdr_length,'flags':flags,'data':data, 'mss':mss} 
    return tcp_dict

def printIPHeader(ip_dict):
    line()
    print "=================================="
    print "Internet Protocol"
    print "=================================="
     
    print 'Version : ' + str(ip_dict['version'])
    print 'IP Header Length : ' + str(ip_dict['iph_length'])
    print 'TTL : ' + str(ip_dict['ttl'])
    print 'Protocol : ' + str(ip_dict['protocol'])
    print 'Source Address : ' +str(ip_dict['src_ip']) 
    print 'Destination Address : ' +str(ip_dict['dest_ip']) 


def printTCPHeader(tcp_dict):
    print "=================================="
    print "Transport Control Protocol"
    print "=================================="
    print 
     
    print 'Source Port : ',tcp_dict['src_port']
    print 'Dest Port : ', tcp_dict['dest_port']
    print 'Sequence Number : ',tcp_dict['sequence']
    print 'Acknowledgement : ',tcp_dict['acknowledgement']
    print 'TCP header length : ',tcp_dict['tcp_hdr_length']
    flags = tcp_dict['flags']
    print "flags ", hex(flags)
    flag_dict = getFlagDict(flags)
    print "syn: ", flag_dict['syn']
    print "ack: ", flag_dict['ack']
    print "fin: ", flag_dict['fin']
    print 'Data : ' + tcp_dict['data']
    line()
    print

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
        tcp_checksum = getChecksum(tmp)
        #tcp_checksum = getChecksum(data)
	return tcp_checksum

def tcp_packet(seqNo,ackNo,src_port,dest_port,src_ip,dest_ip,data,flagDict, use_mss):

        tcp_src_port = src_port
        tcp_dest_port = dest_port
        tcp_seq = seqNo
        tcp_ack_seq = ackNo
        tcp_offset = 5+use_mss
        fin = flagDict['fin']
        syn = flagDict['syn']
        rst = flagDict['rst']
        psh = flagDict['psh']
        ack = flagDict['ack']
        urg = flagDict['urg']
        tcp_window  = socket.htons(5840)
        tcp_checksum=0
        tcp_urg_ptr = 0

        tcp_offset_real = (tcp_offset << 4 ) + 0 
        tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)
        
        tmp_hdr = pack('!HHLLBBHHH' , tcp_src_port,tcp_dest_port,tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags, tcp_window, tcp_checksum, tcp_urg_ptr)
	tcp_checksum = make_tcp_checksum(src_ip,dest_ip,tmp_hdr,data)
        #tcp_checksum = getChecksum(data)

        tcp_header = pack('!HHLLBBH' , tcp_src_port, tcp_dest_port, tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags,  tcp_window) +pack('!H' , tcp_checksum) + pack('!H' , tcp_urg_ptr)
	return tcp_header


def line():
    print '-----------------------------------------------------------------------' 

def make_packet(seqNo,ackNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header):
    use_mss=0
    tcp_header = tcp_packet(seqNo,ackNo, src_port,dest_port,src_ip,dest_ip, data,flags,use_mss)
    return ip_header + tcp_header + data
def make_mssPack():
    mss_type=2
    mss_length=4
    mss_value=client_mss_size
    mss_pack= pack('!BBH',mss_type,mss_length,mss_value)
    return mss_pack

def make_packet_with_mss(seqNo,ackNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header):
    use_mss=1
    tcp_header = tcp_packet(seqNo,ackNo, src_port,dest_port,src_ip,dest_ip, data,flags,use_mss)
    mss_pack = make_mssPack()
    return ip_header + tcp_header + mss_pack +data


def syncronization(packet):
    sock.sendto(packet,(dest_ip, dest_port))
    print "[Send SYN]"
    sequence, acknowledgement = recv_syn_ack(packet)
    return sequence,acknowledgement

def finalization(packet):
    sock.sendto(packet,(dest_ip, dest_port))
    sequence , acknowledgement = recv_fin_ack()
    return sequence,acknowledgement



def sendACK(ip_dict,tcp_dict):
    print "[Send ACK]"
    flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
    recvSeq = tcp_dict['acknowledgement']
    ackSeq  = tcp_dict['sequence']  + 1
    src_port = tcp_dict['dest_port']
    dest_port = tcp_dict['src_port']
    src_ip = ip_dict['dest_ip']
    dest_ip = ip_dict['src_ip']
    data = ''
    ip_header = ip_packet(src_ip,dest_ip) 

    packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
    sock.sendto(packet, (dest_ip,dest_port))


def recv_syn_ack(packet):
    line()
    isSYN=0
    isACK=0
    sequence = 0
    acknowledgement=0
    ip_dict={}
    tcp_dict={}
    global buffer_size
    global client_mss_size
    global server_mss_size 
    backup = packet
    while True:
        try:
            if isSYN==1 and isACK==1:
                break

	    packet= recv_sock.recvfrom(buffer_size+40)
            ip_dict,tcp_dict = unPack_header(packet)    
            if tcp_dict['dest_port'] != src_port: #or tcp_dict['sequence'] == 0:
                  continue
            #printIPHeader(ip_dict)
            #printTCPHeader(tcp_dict)
            line()

            flags = tcp_dict['flags']
            flag_dict= getFlagDict(flags)
            syn = flag_dict['syn']
            ack = flag_dict['ack']
            rst = flag_dict['rst']
            sequence=  tcp_dict['sequence']
            acknowledgement =  tcp_dict['acknowledgement']
          
            if  syn==1:
                print "SYN receive"
                isSYN=1
                server_mss_size = tcp_dict['mss']
                sendACK(ip_dict,tcp_dict)
            elif  ack == 1:
                print "ACK receive"
                isACK=1
            elif  rst == 1:
                print "[Send SYN]"
                sock.sendto(backup,(dest_ip, dest_port))
            line()
        except socket.timeout:
              print "time out, resend! seq No :", sequence
              sock.sendto(backup,(dest_ip, dest_port))
    line()
    return sequence,acknowledgement


def recv_ack(totalFileIndex=1,Buffer=None):
    sequence=0
    acknowledgement=0
    line()
    while True:
        try:
	    packet= recv_sock.recvfrom(buffer_size+40)
            ip_dict,tcp_dict = unPack_header(packet)    
            flags = tcp_dict['flags']
            flag_dict= getFlagDict(flags)
            if tcp_dict['dest_port'] != src_port or tcp_dict['sequence'] ==0 :
                  continue
            #printIPHeader(ip_dict)
            #printTCPHeader(tcp_dict)
            ack = flag_dict['ack']
            rst = flag_dict['rst']
            if ack==1:
                sequence = tcp_dict['sequence']
                acknowledgement= tcp_dict['acknowledgement']
                print "ACK receive"
                break
            elif rst==1 and Buffer is not None:
                sock.sendto(Buffer[(acknowledgement)%totalFileIndex],(dest_ip,dest_port))
        except socket.timeout:
            print "time out, resend! seq No:", sequence
    line()
    return sequence, acknowledgement


def recv_fin_ack():
    line()
    isFIN=0
    isACK=0
    sequence=0
    acknowledgement=0
    while True:
        try:
            if isFIN ==1 and isACK ==1:
                break
	    packet= recv_sock.recvfrom(buffer_size+40)
            ip_dict,tcp_dict = unPack_header(packet)    
            if tcp_dict['dest_port'] != src_port or tcp_dict['sequence'] ==0:
                  continue
            #printIPHeader(ip_dict)
            #printTCPHeader(tcp_dict)
            flags = tcp_dict['flags']
            flag_dict= getFlagDict(flags)
            ack= flag_dict['ack']
            fin= flag_dict['fin']
            sequence= tcp_dict['sequence']
            acknowledgement = tcp_dict['acknowledgement']

            if fin==1:
                print "FIN receive", acknowledgement
                sendACK(ip_dict,tcp_dict)
                isFIN=1
            elif  ack == 1:
                print "ACK receive", acknowledgement
                isACK=1
        except socket.timeout:
              print "time out "
    line()
    return sequence,acknowledgement

def sendData(data, seqNo, nextSeqNo):
    flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
    packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
    sock.sendto(packet,(dest_ip, dest_port))
 

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    recv_sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    #s.settimeout(0.1)
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()


start_time = time.time()

packet = ' '
ip_header = ip_packet(src_ip,dest_ip)

fileSize = os.path.getsize(filePath) 
windowsize=  8
totalFileIndex = fileSize /  windowsize



DataSize = fileSize
maximumSeqSize = int('0xffffffff',16)
if maximumSeqSize < DataSize:
    print "File Size should be less than " , maximumSeqSize , " Byte"
    raise Exception("OverSizeException")
print "Data size is ", DataSize

print "#################################################################"
print "syncronization"
print "#################################################################"
print

seqNo=0
nextSeqNo = seqNo +30
data = ''
flags  = {'fin':0,'syn':1,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet_with_mss(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
sequence,acknowledgement = syncronization(packet)
print 
print 'Server MSS is : ' , server_mss_size
if client_mss_size < server_mss_size:
    buffer_size = client_mss_size
else:
    buffer_size = server_mss_size
print 'Established MSS is : ', buffer_size
print


#filePath
data = filePath
seqNo = acknowledgement
nextSeqNo = seqNo+ len(data)
print "#################################################################"
print "send fileName"
print "FileName : ", filePath
print "#################################################################"
print

flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
sock.sendto(packet,(dest_ip, dest_port))
print "send fileName"
sequence, acknowledgement = recv_ack(totalFileIndex)
print


#fileSize
data = str(fileSize)
seqNo = acknowledgement
nextSeqNo=  seqNo +len(data)
print "#################################################################"
print "send fileSize"
print "FileSize : ", fileSize
print "#################################################################"
print 

flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
sock.sendto(packet,(dest_ip, dest_port))
print "send fileSize"
sequence, acknowledgement = recv_ack(totalFileIndex)
print


print "##################### Selective reapeat-ARQ start ######################"
seqNo = 0
nextSeqNo=seqNo
start_time = time.time()
size=0
Rremain = fileSize
remain = fileSize % buffer_size
Rsize = 0
Buffer = {}
ACKBuffer ={}
wfrom=0
wto=wfrom+windowsize


isSend = {}
isACK = {}

print fileSize
print windowsize
print totalFileIndex

isSend = isSend.fromkeys(range(totalFileIndex+2),[])
isACK= isACK.fromkeys(range(totalFileIndex+2),[])

for i in range(totalFileIndex+2):
    isSend[i].append(0)
    isACK[i].append(0)

with open(filePath, 'rb') as f:
    while True:
        if Rremain== 0 :
            break
        print '#### send Frame ####'
        for i in range(wfrom,wto):
            if i >=totalFileIndex+1:
                continue
            if  isACK[i+1]==1:
                continue
            if isSend[i]==1:
                continue
            seqNo = nextSeqNo
            nextSeqNo = seqNo+ buffer_size
            read_data =f.read(buffer_size)
            flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
            packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,read_data,flags,ip_header)
	    Buffer[i%totalFileIndex] = packet 
            sock.sendto(packet,(dest_ip, dest_port))

        for i in range(wfrom, wto):
            if i >= totalFileIndex +1:
                continue
            if isACK[i+1] ==1:
                continue
            if isSend[i] ==1:
                continue
            print 'send seqNo', i% totalFileIndex
            sock.sendto(Buffer[i%totalFileIndex] ,(dest_ip,dest_port))
            isSend[i]=1
    
        start = wfrom
        end = start+ windowsize        
        print "window start : ",start
        print "window end :", end-1
        try:
            sequence, acknowledgement = recv_ack(totalFileIndex,Buffer)
            index = (sequence) / buffer_size 
            if index in range(start,end+1):
                if isACK[index] ==1:
                 continue
                print "ACK receive", index %totalFileIndex
                if Rremain < buffer_size :
                     Rremain -= remain
                     Rsize += remain
                else:
                    Rremain-=buffer_size
                    Rsize += buffer_size
                print Rsize , "/",fileSize , "(Currentsize/Totalsize) , ", round((100.00 * Rsize/int(fileSize)),2), "%"
                
            isACK[index % totalFileIndex] =1
            #window move
            if index==wfrom+1:
                n=index
                while True:
                    if n >=totalFileIndex+1:
                        break
                    if isACK[n] == 1:
                       wfrom+=1
                       wto+=1
                       n+=1
                    else:
                       break 
            else:
                if isACK[index+1] ==1:
                    continue
                print "NAK receive", index%totalFileIndex
                print "resend!",index%totalFileIndex
                sock.sendto(Buffer[(index-1)%totalFileIndex],(dest_ip,dest_port))
    ### time out ###
        except socket.timeout:
            for i in range (start, end):
                if i>= fileSize+1:
                    break 
                if isACK[i+1] ==1:
                    continue
                if isSend[i] ==1:
                    print "Timeout , resend! from seqNo",i%totalFileIndex
                    sock.sendto(Buffer[i%totalFileIndex],(dest_ip,dest_port))
                    continue

print "##################### Selective reapeat-ARQ end ######################"
        

'''
print "##################### Stop and waitreapeat-ARQ start ######################"
with open(filePath, 'rb') as f:
    while True:
      if remain >= buffer_size:
        remain -=buffer_size
        data = f.read(buffer_size)
        size += buffer_size
        print size , "/",fileSize , "(Currentsize/Totalsize) , ", round((100.00 * size/int(fileSize)),2), "%"
        flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
        packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
        sock.sendto(packet,(dest_ip, dest_port))
        time.sleep(1/20.0)

      else:
        size+=remain
        data = f.read(remain)
        print size , "/",fileSize , "(Currentsize/Totalsize) , ", round((100.00 * size/int(fileSize)),2), "%"
        flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
        packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
        sock.sendto(packet,(dest_ip, dest_port))
        time.sleep(1/20.0)

        print "Completed ..."
        break
    end_time = time.time()
    print "Time elapsed : ", end_time - start_time
print "##################### Stop and waitreapeat-ARQ end ######################"
'''

seqNo =acknowledgement 
nextSeqNo = seqNo+30
print "#################################################################"
print "finalization"
print "#################################################################"
print
print "[Send FIN]"
data = ''
flags  = {'fin':1,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,nextSeqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
sequence , acknowledgement = finalization(packet)
print

end_time=time.time()

print "Time elapsed : ", end_time - start_time

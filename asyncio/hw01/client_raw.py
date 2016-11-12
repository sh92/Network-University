import socket, sys
from struct import *
import hashlib
import os
import time
import threading

buffer_size = 1500
filePath = sys.argv[1]
'''
dest_ip = sys.argv[1]
dest_port = int(sys.argv[2])
filePath = sys.argv[3]

if len(sys.argv) < 3:
	print '[Dest IP Addr] [Dest Port] [File Path]'
	sys.exit()
'''

def printPacket(packet):
    packet= packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8]);
    d_addr = socket.inet_ntoa(iph[9]);
     
    tcp_header = packet[iph_length:iph_length+20]
    #now unpack them :)
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    flags = tcph[5]
    cwr = (flags & 0x80) >> 7
    ece = (flags & 0x40) >> 6
    urg = (flags & 0x20) >> 5
    ack = (flags & 0x10) >> 4
    psh = (flags & 0x8) >> 3
    rst = (flags & 0x4) >> 2
    syn = (flags & 0x2) >> 1
    fin = (flags & 0x1) 
    line()
    print "sequence" , sequence
    print "acknowledgement",acknowledgement
    print "flags ",hex(flags)
    print "ack ",ack
    print "syn ",syn
    print "fin ",fin
    line()
     
    #print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)
     
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
     
    #get data from the packet
    data = packet[h_size:]
    #print 'Data : ' + data
    #print
    return sequence,acknowledgement,syn,ack,fin

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

def tcp_packet(seqNo,src_port,dest_port,src_ip,dest_ip,data,falgs):

        tcp_src_port = src_port
        tcp_dest_port = dest_port
        tcp_seq = seqNo
        tcp_ack_seq = seqNo+1
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


def line():
    print '-----------------------------------------------------------------------' 

def make_packet(seqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header):
    tcp_header = tcp_packet(seqNo, src_port,dest_port,src_ip,dest_ip, data,flags)
    return ip_header + tcp_header + data



def syncronization(packet,seqNo):
    sock.sendto(packet,(dest_ip, 0))
    recv_syn_ack(packet,seqNo)

def finalization(packet,serNo):
    sock.sendto(packet,(dest_ip, 0))
    recv_fin_ack(packet,seqNo)

def send_Data(packet,seqNo):
    sock.sendto(packet,(dest_ip, 0))
    #threading.Thread(target = recv_ack, args=(sock)).start()

def recv_syn_ack(packet,seqNo):
    line()
    isSYN=0
    isACK=0
    while True:
        try:
            if isSYN==1 and isACK==1:
                break
	    Reply= recv_sock.recvfrom(buffer_size)
	    recv_sequence,recv_ack,syn,ack,fin = printPacket(Reply)
            line()
            if  syn==1:
                flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
                packet = make_packet(recv_ack+1,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
                send_Data(packet,recv_ack)
                print "SYN receive", recv_ack
                isSYN=1
            elif  ack == 1:
                print "ACK receive", recv_ack
                isACK=1
            line()
        except socket.timeout:
              print "time out, resend! seq No:",seqNo
              sock.sendto(packet,(dest_ip, 0))
    line()

def recv_ack(packet,seqNo):
    line()
    while True:
        try:
	    Reply= recv_sock.recvfrom(buffer_size)
	    recv_sequence,recv_ack,syn,ack,fin = printPacket(Reply)
            print "SeqNo" , seqNo
            print "recv_sequence ",recv_sequence
            print "recv_ack",recv_ack
            print "ack ",ack
            print "syn ",syn
            print "fin ",fin
            if  ack == 1:
                print "ACK receive", recv_ack
                break
        except socket.timeout:
              print "time out, resend! seq No:",seqNo
              sock.sendto(packet,(dest_ip, 0))
    line()


def recv_fin_ack(packet,seqNo):
    line()
    isFIN=0
    isACK=0
    while True:
        try:
            if isFIN ==1 and isACK ==1:
                break
	    Reply= recv_sock.recvfrom(buffer_size)
	    recv_sequence,recv_ack,syn,ack,fin = printPacket(Reply)
            print "SeqNo" , seqNo
            print "recv_sequence ",recv_sequence
            print "recv_ack",recv_ack
            print "ack ",ack
            print "syn ",syn
            print "fin ",fin
            if fin==1:
                flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
                packet = make_packet(recv_ack+1,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
                send_Data(packet,recv_ack)
                print "FIN receive", recv_ack
                isFIN=1
            elif  ack == 1:
                print "ACK receive", recv_ack
                isACK=1
        except socket.timeout:
              print "time out, resend! seq No:",seqNo
              sock.sendto(packet,(dest_ip, 0))
    line()
 

def receive_data(packet,seqNo):
    print '-----------------------------------------------------------------------' 
    while True:
        try:
	    Reply= recv_sock.recvfrom(buffer_size)
	    recv_sequence,recv_ack,syn,ack,fin = printPacket(Reply)
            print "SeqNo" , seqNo
            print "recv_sequence ",recv_sequence
            print "recv_ack",recv_ack
            print "ack ",ack
            print "syn ",syn
            print "fin ",fin
            if  syn==1:
                flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
                packet = make_packet(recv_ack+1,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
                send_Data(packet,recv_ack)
                print "SYN receive", recv_ack
                break
            elif fin==1:
                flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
                packet = make_packet(recv_ack+1,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
                send_Data(packet,recv_ack)
                print "FIN receive", recv_ack
                break
            elif  ack == 1:
                print "ACK receive", recv_ack
                break
            else:
                print "NAK receive",seqNo
        except socket.timeout:
              print "time out, resend! seq No:",seqNo
              sock.sendto(packet,(dest_ip, 0))
    print '-----------------------------------------------------------------------' 

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    recv_sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    #s.settimeout(0.1)
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
print "Data size is ", DataSize

seqNo=0
print "#################################################################"
print "syncronization"
print "#################################################################"
print
data = ''
flags  = {'fin':0,'syn':1,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
syncronization(packet,seqNo)
print

nextSeqNo = seqNo +1
seqNo = nextSeqNo

#filePath
data = filePath
print "#################################################################"
print "send filePath"
print "FileName : ", filePath
print "#################################################################"
print
flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
send_Data(packet,seqNo)
recv_ack(packet,seqNo)
print


nextSeqNo = seqNo + 1
seqNo = nextSeqNo

'''
#filesize
data = str(filesize)
print "#################################################################"
print "send fileSize"
print "FileSize : ", filesize
print "#################################################################"
print 
nextSeqNo=  seqNo +len(data)
flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
send_Data(packet,seqNo)
print

nextSeqNo = seqNo + len(data)
seqNo = nextSeqNo
'''



print "#################################################################"
print "finalization"
print "#################################################################"
print
data = ''
flags  = {'fin':1,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
packet = make_packet(seqNo,src_port,dest_port,src_ip,dest_ip,data,flags,ip_header)
finalization(packet,seqNo)
print


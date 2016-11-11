import socket, sys
from struct import *
import hashlib
import os
import time

buffer_size = 65565

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

def tcp_packet(seq,ackSeq,src_port,dest_port,src_ip,dest_ip,data,flags):

        tcp_src_port = src_port
        tcp_dest_port = dest_port
        tcp_seq = seq
        tcp_ack_seq = seq+len(data)
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


def make_packet(seq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header):
    data=''
    tcp_header = tcp_packet(seq,ackSeq ,src_port,dest_port,src_ip,dest_ip,data,flags)
    return ip_header + tcp_header + data

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
     
    print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
     
    tcp_header = packet[iph_length:iph_length+20]
     
    #now unpack them :)
    tcph = unpack('!HHLLBBHHH' , tcp_header)
     
    src_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
     
    print 'Source Port : ' + str(src_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)
     
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
     
    #get data from the packet
    data = packet[h_size:]
    print 'Data : ' + data
    print
    return sequence,acknowledgement,data, s_addr, d_addr, src_port,dest_port,ip_header
   

def receiveData(seq):
    prev_seq =seq
    while True:
         try:
              packet= sock.recvfrom(buffer_size)
	      recvSeq,ackSeq,data,src_ip, dest_ip, src_port,dest_port,ip_header= printPacket(packet)
	      print recvSeq
              if recvSeq == seq:
                   "print ACK!!"
                   flags = {'fin':0,'syn':1,'rst':0,'psh':0,'ack':1,'urg':0}
                   packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
                   sock.sendto(packet,(dest_ip,dest_port))
                   break
              else:
                   flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
                   ackSeq = 0 
                   packet = make_packet(prev_seq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
#                   sock.sendto(packet, (dest_ip,dest_port))
                   print "NAK", prev_seq
         except socket.timeout:
              flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
              ackSeq = 0 
              packet = make_packet(prev_seq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
              print "retransmit NAK packet"
 #             sock.sendto(pacekt, (dest_ip,dest_port))
    return data ,ackSeq 

try:
    sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    #sock.bind((ServerIP,ServerPort)) 
    #sock.settimeout(0.1)
    print "ready for client ... "
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()


seq=0
fileName,ackSeq = receiveData(seq)
print seq
seq = ackSeq
'''
fileSize,ackSeq = receiveData(seq)
seq = ackSeq
print seq
'''

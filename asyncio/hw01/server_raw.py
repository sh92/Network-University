import socket, sys
from struct import *
import hashlib
import os
import time

buffer_size = 1500

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
        tcp_ack_seq = ackSeq
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

    line()
    print "=================================="
    print "Internet Protocol"
    print "=================================="
     
    print 'Version : ' + str(version)
    print 'IP Header Length : ' + str(ihl)
    print 'TTL : ' + str(ttl)
    print 'Protocol : ' + str(protocol)
    print 'Source Address : ' + str(s_addr)
    print 'Destination Address : ' + str(d_addr)
     
    tcp_header = packet[iph_length:iph_length+20]
     
    #now unpack them :)
    tcp_hdr = unpack('!HHLLBBHHH' , tcp_header)
     
    src_port = tcp_hdr[0]
    dest_port = tcp_hdr[1]
    sequence = tcp_hdr[2]
    acknowledgement = tcp_hdr[3]
    doff_reserved = tcp_hdr[4]
    tcp_hdr_length = doff_reserved >> 4
    flags = tcp_hdr[5]
    cwr = (flags & 0x80) >> 7
    ece = (flags & 0x40) >> 6
    urg = (flags & 0x20) >> 5
    ack = (flags & 0x10) >> 4
    psh = (flags & 0x8) >> 3
    rst = (flags & 0x4) >> 2
    syn = (flags & 0x2) >> 1
    fin = (flags & 0x1) 

    print "=================================="
    print "Transport Control Protocol"
    print "=================================="
    print 
    print "flags ", hex(flags)
    print "syn: ", syn
    print "ack: ", ack
    print "fin: ", fin
     
    print 'Source Port : ' + str(src_port) 
    print 'Dest Port : ' + str(dest_port) 
    print 'Sequence Number : ' + str(sequence) 
    print 'Acknowledgement : ' + str(acknowledgement) 
    print 'TCP header length : ' + str(tcp_hdr_length)
     
    h_size = iph_length + tcp_hdr_length * 4
    data_size = len(packet) - h_size
     
    #get data from the packet
    data = packet[h_size:]
    print 'Data : ' + data
    line()
    print
    return sequence,acknowledgement,data, s_addr, d_addr, src_port,dest_port,ip_header,syn,ack,fin

def line():
    print '-----------------------------------------------------------------------' 
def arrow_line():
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

def syncronization():
    recv_syn()
    recv_ack()

def finalization():
    recv_fin()
    recv_ack()


def recv_fin():
    arrow_line()
    print "Fin Wating ..."
    while True:
         try:
              packet= sock.recvfrom(buffer_size)
	      recvSeq,ackSeq,data,src_ip, dest_ip, src_port,dest_port,ip_header, syn, ack, fin= printPacket(packet)
              if fin==1 :
                   print "[Receive FIN]"
                   print
                   print "send ACK"
                   ackSeq  =  recvSeq + 1
                   flags = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
                   packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
                   sock.sendto(packet,(dest_ip,dest_port))


                   print "[Send FIN]"
                   recvSeq = recvSeq + 10
                   flags = {'fin':1,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
                   packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
                   sock.sendto(packet,(dest_ip,dest_port))
                   break
         except socket.timeout:
              print "retransmit NAK packet"


def recv_syn():
    arrow_line()
    print "SYN Wating ..."
    while True:
         try:
              packet= sock.recvfrom(buffer_size)
	      recvSeq,ackSeq,data,src_ip, dest_ip, src_port,dest_port,ip_header, syn, ack, fin= printPacket(packet)
              if syn==1 :
                   print "[Receive SYN]"
                   print

                   print '[Send ACK]'
                   flags = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
                   ackSeq  =  recvSeq + 1
                   packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
                   sock.sendto(packet,(dest_ip,dest_port))

                   print '[Send SYN]'
                   recvSeq = recvSeq + 10
                   flags = {'fin':0,'syn':1,'rst':0,'psh':0,'ack':0,'urg':0}
                   packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
                   sock.sendto(packet,(dest_ip,dest_port))
                   break
         except socket.timeout:
              print "retransmit NAK packet"


def recv_ack():
    arrow_line()
    print "ACK Wating ..."
    while True:
        try:
            packet= sock.recvfrom(buffer_size)
	    recvSeq,ackSeq,data,src_ip, dest_ip, src_port,dest_port,ip_header, syn, ack, fin= printPacket(packet)
            if  ack == 1:
                print "[Receive ACK]", recvSeq
                break
        except socket.timeout:
              print "time out, resend! seq No:",seqNo

def receiveData():
    line()
    try:
        packet= sock.recvfrom(buffer_size)
        recvSeq,ackSeq,data,src_ip, dest_ip, src_port,dest_port,ip_header, syn, ack, fin= printPacket(packet)
        print "send ACK"
        flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
        ackSeq  =  recvSeq + 1
        recvSeq = recvSeq + 10
        packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
        sock.sendto(packet, (dest_ip,dest_port))
        print
    except socket.timeout:
        print "retransmit NAK packet"
    line()
    recv_ack()
    return data 

try:
    sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    #sock.bind((ServerIP,ServerPort)) 
    #sock.settimeout(0.1)
    print "ready for client ... "
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()


print "############################################################"
print"Syncronization"
print "############################################################"
syncronization()
print 

print "############################################################"
print"fileName"
print "############################################################"
fileName= receiveData()
print

'''
print "############################################################"
print"fileSize"
print "############################################################"
fileSize= receiveData()
print
'''

print "############################################################"
print"finalization"
print "############################################################"
finalization()
print

'''
fileSize,ackSeq = receiveData(seq)
seq = ackSeq
print seq
'''

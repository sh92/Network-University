import socket, sys
from struct import *
import hashlib
import os
import time

buffer_size = 65565

if len(sys.argv) < 1:
	print '[Port]'
	sys.exit()


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
     
    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
     
    print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)
     
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
     
    #get data from the packet
    data = packet[h_size:]
    print 'Data : ' + data
    print
    return sequence,data, s_addr, d_addr, source_port,dest_port
   

try:
    sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    #sock.bind((ServerIP,ServerPort)) 
    #sock.settimeout(0.1)
    print "ready for client ... "
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()

seqNo=0
ACK = "ACK"+str(seqNo+1)
NAK = "NAK"+str(seqNo)
print seqNo
fileName=''
while True:
    try:
        packet= sock.recvfrom(buffer_size)
	packetSeq,fileName,source_ip, dest_ip, source_port,dest_port= printPacket(packet)
	print packetSeq
        if packetSeq== seqNo:
            sock.sendto(ACK,(dest_ip,dest_port))
            break
        else:
            sock.sendto(NAK, (dest_ip,dest_port))
            print "NAK", seqNo
    except socket.timeout:
        print "retransmit NAK packet"
        sock.sendto(NAK, (dest_ip,dest_port))


print fileName
seqNo = len(fileName) + seqNo
print seqNo
fileSize=0
ACK = "ACK"+str(seqNo+1)
NAK = "NAK"+str(seqNo)

while True:
    try:
        packet= sock.recvfrom(buffer_size)
	packetSeq,fileName,source_ip, dest_ip, source_port,dest_port= printPacket(packet)
	print packetSeq
        if packetSeq== seqNo:
            sock.sendto(ACK,(dest_ip,dest_port))
            break
        else:
            sock.sendto(NAK, (dest_ip,dest_port))
            print "NAK", seqNo
    except socket.timeout:
        print "retransmit NAK packet"
        sock.sendto(NAK, (dest_ip,dest_port))

print fileSize

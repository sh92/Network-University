import socket, sys
from struct import *


# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0
     
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w
     
    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);
     
    #complement and mask to 4 byte short
    s = ~s & 0xffff
     
    return s

try:
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()


packet = ' '

source_ip = '127.0.0.1'
dest_ip = '127.0.0.1'


#ip header
ip_ihl = 5
ip_ver = 4
ip_tos = 0 
ip_tot_len = 0
ip_packet_id = 12345
ip_frag_off = 0
ip_ttl = 255
ip_proto = socket.IPPROTO_TCP
ip_checksum = 0
ip_saddr = socket.inet_aton(source_ip)
ip_daddr = socket.inet_aton(dest_ip)

ip_header = pack('!BBHHHBBH4s4s',ip_ver, ip_ihl,ip_tos, ip_packet_id, ip_frag_off,ip_ttl, ip_proto,ip_checksum,ip_saddr,ip_daddr)

#tcp header
tcp_src_port = 1234
tcp_dst_port = 80
tcp_seq = 454
tcp_ack_seq = 0 
tcp_offset = 5
fin = 0 
syn = 1
rst = 0
psh = 0
ack = 0
urg = 0
tcp_window  = socket.htons(5840)
tcp_checksum=0
tcp_urg_ptr = 0

tcp_offset_real = (tcp_offset << 4 ) + 0 
tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)
tcp_header = pack('!HHLLBBHHH' , tcp_src_port,tcp_dst_port,tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags, tcp_window, tcp_checksum, tcp_urg_ptr)

data = 'Hello, how are you'

src_addr = socket.inet_aton(source_ip)
dest_addr = socket.inet_aton(dest_ip)
placeholder=0
protocol = socket.IPPROTO_TCP
tcp_len = len(tcp_header) + len(data)

psh = pack('!4s4sBBH', src_addr, dest_addr , placeholder, protocol, tcp_len)
psh = psh  + tcp_header + data
 
tcp_checksum= checksum(psh)
print tcp_checksum

tcp_header= pack('!HHLLBBH' , tcp_src_port, tcp_dst_port, tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags,  tcp_window) +pack('H' , tcp_checksum) + pack('!H' , tcp_urg_ptr)

packet = ip_header + tcp_header + data
s.sendto(packet, (dest_ip, 0))


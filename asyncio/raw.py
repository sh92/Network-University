import socket
import struct

ihl = 5
ihl_version = 4
tos = 0
tot_len = 20
id = 35123
frag_off = 0 
ttl = 64
protocol = socket.IPPROTO_TCP
check = 12111
source_ip = "127.0.0.1"
dest_ip = "192.168.0.6"
saddr = socket.inet_aton ( source_ip )
daddr = socket.inet_aton ( dest_ip )

ip_header = struct.pack('!BBHHHBBH4s4s', ihl_version,tos,tot_len,id, frag_off, ttl, protocol, check,saddr, daddr)

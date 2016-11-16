import socket, sys
from struct import *
import hashlib
import os
import time
from calc_md5 import md5Check


if len(sys.argv) < 2:
    print("[PORT] [server mss size]")
    sys.exit()

buffer_size =1460
RAW_IP = ''
RAW_PORT = int(sys.argv[1])
server_mss_size = int(sys.argv[2])
client_mss_size = 0

print "ready for client ... "

try:
    sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sock.bind((RAW_IP,RAW_PORT)) 
except socket.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()
try:
    send_sock=socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except send_sock.error , msg:
    print "Scoket could not be creadted. Erorr Code : " + str(msg[0]) + ' Message ' +msg[1]
    sys.exit()



def getChecksum(data):
    sum=0
    for i in range(0, len(data), 2):
        if i+1 < len(data):
            data16= ord(data[i]) + (ord(data[i+1]) << 8) 
            tempSum = sum + data16 
            sum = (tempSum & 0xffff) + (tempSum >> 16)    
    return ~sum & 0xffff

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

def ip_packet(src_ip,dest_ip):
	ip_ihl = 5
	ip_ver = 4
	ip_tos = 0 
	ip_tot_len = 0
	ip_packet_id = 54321
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
	return tcp_checksum

def make_tcp_checksum_data(src_ip,dest_ip,tmp_hdr,data):
        src_addr = socket.inet_aton(src_ip)
        dest_addr = socket.inet_aton(dest_ip)
        placeholder=0
        protocol = socket.IPPROTO_TCP
        tcp_len = len(tmp_hdr) + len(data)

        pseudo_hdr= pack('!4s4sBBH', src_addr, dest_addr , placeholder, protocol, tcp_len)
        tmp = pseudo_hdr + tmp_hdr +data
	return tmp

def tcp_packet(seq,ackSeq,src_port,dest_port,src_ip,dest_ip,data,flagDict,use_mss):
        tcp_src_port = src_port

def tcp_packet(seq,ackSeq,src_port,dest_port,src_ip,dest_ip,data,flagDict,use_mss):
        tcp_src_port = src_port
        tcp_dest_port = dest_port
        tcp_seq = seq
        tcp_ack_seq = ackSeq
        tcp_offset = 5 + use_mss
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

        tcp_header = pack('!HHLLBBH' , tcp_src_port, tcp_dest_port, tcp_seq, tcp_ack_seq, tcp_offset_real, tcp_flags,  tcp_window) +pack('!H' , tcp_checksum) + pack('!H' , tcp_urg_ptr)
	return tcp_header

def mss_packet():
    mss_type = 2
    mss_length = 4
    mss_value = server_mss_size 
    mss_pack = pack('!BBH', mss_type, mss_length,mss_value)
    return mss_pack


def make_packet_with_mss(seq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header):
    data=''
    use_mss=1
    tcp_header = tcp_packet(seq,ackSeq ,src_port,dest_port,src_ip,dest_ip,data,flags, use_mss)
    mss_pack = mss_packet()
    return ip_header + tcp_header + mss_pack +data

def make_packet(seq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header):
    data=''
    use_mss=0
    tcp_header = tcp_packet(seq,ackSeq ,src_port,dest_port,src_ip,dest_ip,data,flags,use_mss)
    return ip_header + tcp_header  +data

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

def unPack_header(packet):
    ip_dict = unPackIP_header(packet)
    tcp_dict = unPackTCP_header(packet,ip_dict)
    return ip_dict, tcp_dict

def unPackIP_header(packet):
    packet= packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    identification = iph[3]
    flag_off = iph[4]
    ttl = iph[5]
    protocol = iph[6]
    src_ip= socket.inet_ntoa(iph[8]);
    dest_ip= socket.inet_ntoa(iph[9]);
    ip_dict = {'iph_length':iph_length,'version':version,'ttl':ttl,'protocol':protocol,'src_ip':src_ip,'dest_ip':dest_ip , 'identification':identification}
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

def unPackTCP_header(packet,ip_dict):
    iph_length = ip_dict['iph_length']
    src_ip  = ip_dict['src_ip']
    dest_ip = ip_dict['dest_ip']

    packet= packet[0]
    tcp_header = packet[iph_length:iph_length+20]
    tcp_hdr = unpack('!HHLLBBHHH' , tcp_header)
     
    src_port = tcp_hdr[0]
    dest_port = tcp_hdr[1]
    sequence = tcp_hdr[2]
    acknowledgement = tcp_hdr[3]
    dataoff_reserved = tcp_hdr[4]
    tcp_hdr_length = dataoff_reserved >> 4
    flags = tcp_hdr[5]
    window_size = tcp_hdr[6]
    checksum = tcp_hdr[7]
    urg_ptr = tcp_hdr[8]

    data_start_point = iph_length + tcp_hdr_length * 4
    data_size = len(packet) - data_start_point
    mss=0
    if tcp_hdr_length == 6 :
         option_pack = packet[iph_length+20:data_start_point]
         option_hdr = unpack('!BBH',option_pack)
         option_type = option_hdr[0]
         if option_type == 2:
             mss = option_hdr[2]
    data = packet[data_start_point:]

    tcp_real_offset = (tcp_hdr_length << 4) + 0
    tmp_checksum=0
    tmp_urg_ptr= 0
   
    #get checkSum 
    tmp_hdr = pack('!HHLLBBHHH' , src_port,dest_port,sequence, acknowledgement,tcp_real_offset , flags, window_size, tmp_checksum, tmp_urg_ptr)
    checksum_data = make_tcp_checksum_data(src_ip,dest_ip,tmp_hdr,data)

    tcp_dict = {'src_port':src_port,'dest_port':dest_port,'sequence':sequence,'acknowledgement':acknowledgement,'tcp_hdr_length':tcp_hdr_length,'flags':flags,'data':data , 'mss':mss, 'window_size':window_size,'checksum':checksum, 'checksum_data':checksum_data}
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
    print 'Identification : ' +str(ip_dict['identification'])


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

def line():
    print '-----------------------------------------------------------------------' 
def arrow_line():
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

def syncronization():
    recv_syn()
    recv_ack()
    global buffer_size
    print 'Client MSS is ' ,client_mss_size
    if server_mss_size < client_mss_size:
         buffer_size = server_mss_size
    else:
         buffer_size = client_mss_size
    print 'Established MSS is', buffer_size

def finalization():
    recv_fin()
    recv_ack()

def sendSYN(ip_dict,tcp_dict):
    flags  = {'fin':0,'syn':1,'rst':0,'psh':0,'ack':0,'urg':0}
    sequence = tcp_dict['sequence']
    recvSeq = tcp_dict['acknowledgement'] 
    ackSeq  = sequence+1
 
 
    src_port = tcp_dict['dest_port']
    dest_port = tcp_dict['src_port']
    src_ip = ip_dict['dest_ip']
    dest_ip = ip_dict['src_ip']

    ip_header = ip_packet(src_ip,dest_ip) 

    packet = make_packet_with_mss(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
    send_sock.sendto(packet, (dest_ip,dest_port))


def sendFIN(ip_dict,tcp_dict):
    flags  = {'fin':1,'syn':0,'rst':0,'psh':0,'ack':0,'urg':0}
    ackSeq  = tcp_dict['sequence']+1
    recvSeq = tcp_dict['acknowledgement'] 
    src_port = tcp_dict['dest_port']
    dest_port = tcp_dict['src_port']
    src_ip = ip_dict['dest_ip']
    dest_ip = ip_dict['src_ip']
    ip_header = ip_packet(src_ip,dest_ip) 

    packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
    send_sock.sendto(packet, (dest_ip,dest_port))


def sendACK(ip_dict,tcp_dict):
    flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
    ackSeq  = tcp_dict['sequence']+1
    recvSeq = tcp_dict['acknowledgement'] 
    src_port = tcp_dict['dest_port']
    dest_port = tcp_dict['src_port']
    src_ip = ip_dict['dest_ip']
    dest_ip = ip_dict['src_ip']
    ip_header = ip_packet(src_ip,dest_ip) 

    packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
    send_sock.sendto(packet, (dest_ip,dest_port))


def sendRST(ip_dict,tcp_dict,buffer_no):
    flags  = {'fin':0,'syn':0,'rst':1,'psh':0,'ack':0,'urg':0}
    ackSeq  = tcp_dict['sequence']
    recvSeq = tcp_dict['acknowledgement'] 
    src_port = tcp_dict['dest_port']
    dest_port = tcp_dict['src_port']
    src_ip = ip_dict['dest_ip']
    dest_ip = ip_dict['src_ip']
    ip_header = ip_packet(src_ip,dest_ip) 

    packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
    send_sock.sendto(packet, (dest_ip,dest_port))


def sendACK(ip_dict,tcp_dict):
    flags  = {'fin':0,'syn':0,'rst':0,'psh':0,'ack':1,'urg':0}
    ackSeq  = tcp_dict['sequence']+1
    recvSeq = tcp_dict['acknowledgement'] 
    src_port = tcp_dict['dest_port']
    dest_port = tcp_dict['src_port']
    src_ip = ip_dict['dest_ip']
    dest_ip = ip_dict['src_ip']
    ip_header = ip_packet(src_ip,dest_ip) 

    packet = make_packet(recvSeq,ackSeq,src_port,dest_port,src_ip,dest_ip,flags,ip_header)
    send_sock.sendto(packet, (dest_ip,dest_port))



def recv_fin():
    arrow_line()
#    print "Fin Wating ..."
    while True:
         try:
              packet= sock.recvfrom(buffer_size+40)
              ip_dict , tcp_dict= unPack_header(packet)
              if tcp_dict['dest_port'] != RAW_PORT or ip_dict['identification']!=12345:
                  continue
              #printIPHeader(ip_dict)
              #printTCPHeader(tcp_dict)
              flags = tcp_dict['flags']
              flag_dict= getFlagDict(flags)
              fin  = flag_dict['fin']
              if fin ==1: 
#                   print "[Receive FIN]"
#                   print "Send ACK"
                   sendACK(ip_dict,tcp_dict)

#                   print "[Send FIN]"
                   sendFIN(ip_dict,tcp_dict)
                   break
         except socket.timeout:
              print "retransmit NAK packet"


def recv_syn():
    arrow_line()
#    print "SYN Wating ..."
    global buffer_size
    global client_mss_size
    global server_mss_size
    while True:
         try:
              packet= sock.recvfrom(buffer_size+40)
              ip_dict , tcp_dict= unPack_header(packet)
              if tcp_dict['dest_port'] != RAW_PORT or ip_dict['identification'] !=12345:
                  continue
              #printIPHeader(ip_dict)
              #printTCPHeader(tcp_dict)
              flags = tcp_dict['flags']
              flag_dict= getFlagDict(flags)
              syn = flag_dict['syn']
              if syn==1:
                   client_mss_size = tcp_dict['mss']
#                   print "[Receive SYN]"
#                   print '[Send ACK]'
                   sendACK(ip_dict,tcp_dict)
#                   print '[Send SYN]'
                   sendSYN(ip_dict,tcp_dict)
                   break
         except socket.timeout:
              print "retransmit NAK packet"


def recv_ack():
    arrow_line()
    print "ACK Wating ..."
    while True:
        try:
            packet= sock.recvfrom(buffer_size+40)
            ip_dict , tcp_dict= unPack_header(packet)
            if tcp_dict['dest_port'] != RAW_PORT or ip_dict['identification'] !=12345:
                continue
            #printIPHeader(ip_dict)
            #printTCPHeader(tcp_dict)
            flags = tcp_dict['flags']
            flag_dict= getFlagDict(flags)
            ack = flag_dict['ack']
            if ack == 1:
#                print "[Receive ACK]", tcp_dict['sequence']
                break
        except socket.timeout:
              print "time out, resend! seq No:", stcp_dict['sequence']


def receiveData():
    #line()
    while True:
        try:
            packet= sock.recvfrom(buffer_size+40)
            ip_dict , tcp_dict= unPack_header(packet)
            if tcp_dict['dest_port'] != RAW_PORT or ip_dict['identification'] !=12345:
                continue
            #printIPHeader(ip_dict)
            #printTCPHeader(tcp_dict)
#            print "send ACK"
            sendACK(ip_dict,tcp_dict)
            print
            break
        except socket.timeout:
            print "retransmit NAK packet"
    #line()
    return tcp_dict['data']
print "############################################################"
print"Syncronization"
print "############################################################"
syncronization()

print "############################################################"
print"fileName"
print "############################################################"
fileName= receiveData()

print "############################################################"
print"fileSize"
print "############################################################"
print
fileSize= receiveData()
print



print '####################### selctive-repeat ARQ ################################'
size = 0
remain= int(fileSize)

# window size ande seq size
seqsize= remain/ buffer_size
windowsize = 8

print "window size is ", windowsize
print "seqsize is ", seqsize
wfrom = 0
wto = wfrom + windowsize

start_time = time.time()
Buffer={}
ACK_BUFFER={}
isACK = {}
isACK = isACK.fromkeys(range(seqsize+2),[])
lastframe = int(fileSize) % buffer_size


for i in range(seqsize+2):
    isACK[i].append(0)
while True:
    with open(fileName, "ab") as f:
            if remain== 0:
                for i in range(wfrom,seqsize+1):
                    f.write(Buffer[i%seqsize])
                print "Completed ...."
                break
                
            framesize = buffer_size

            packet= sock.recvfrom(buffer_size+40)
            ip_dict , tcp_dict= unPack_header(packet)
            if tcp_dict['dest_port'] != RAW_PORT or ip_dict['identification'] !=12345:
                continue
            #printIPHeader(ip_dict)
            #printTCPHeader(tcp_dict)

            sequence= tcp_dict['sequence']
            acknowledgement= tcp_dict['acknowledgement']
            checksum = tcp_dict['checksum']
            checksum_data = tcp_dict['checksum_data']

            if verifyChecksum(checksum_data,checksum) == False:
#                print "Checksum is False"
#                print "NAK", sequence
                sendRST(ip_dict,tcp_dict,sequence)
                continue

            BufferNo = sequence/ buffer_size
             
#            print "BufferNo:" ,BufferNo
#            print "seqNo:" ,BufferNo%seqsize
#            print "window start : ",wfrom
#            print "window end : ", wto -1
            
            if BufferNo in range(wfrom,wto):
                if BufferNo > seqsize:
                    continue 
                if isACK[BufferNo] !=1:
                    if BufferNo == seqsize-1:
                        size += lastframe
                        remain -= lastframe
                    else:    
                        size += framesize
                        remain -= framesize
                    print size ,"/", fileSize ," (currentsize/totalsize) ,", round((100.00 *size/int(fileSize)),2) ,"%"
                #time.sleep(1)
                Buffer[BufferNo%seqsize] = tcp_dict['data']
                isACK[BufferNo]=1
                if BufferNo==wfrom:
                    n=BufferNo
                    while True:
                        if n >= seqsize+1:
                            break
                        if isACK[n] == 1:
                            f.write(Buffer[n % seqsize])
                            wfrom+=1
                            wto+=1
                            n+=1
                        else:
                            break 
                ACK_BUFFER[BufferNo] = packet
                sendACK(ip_dict,tcp_dict)
#                print "send ACK",str(BufferNo%seqsize) 
            else:
                if isACK[BufferNo] == 1:
                    tmp_pack = ACK_BUFFER[BufferNo]
                    ip_dict,tcp_dict = unPack_header(tmp_pack)
                    sendACK(ip_dict,tcp_dict)
                    continue
#                print "NAK",BufferNo%seqsize
                sendRST(ip_dict,tcp_dict,BufferNo)

end_time = time.time()
print "Time elapsed : ", end_time - start_time
print '####################### selctive-repeat ARQ ################################'
print 
print "############################################################"
print"finalization"
print "############################################################"
finalization()
print

m = md5Check(fileName)
print(m.calc_md5())

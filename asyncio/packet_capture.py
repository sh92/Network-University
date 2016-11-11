import socket
import struct

socket= socket.socket(socket.AF_PACKET,  socket.SOCK_RAW, socket.ntohs(0x0003))

class Mac():
    def __init__(self,mac):
        self.mac=mac
    def __str__(self):
        return "%s:%s:%s:%s:%s:%s" %(
                self.mac[0:2],
                self.mac[2:4],
                self.mac[4:6],
                self.mac[6:8],
                self.mac[8:10],
                self.mac[10:12]
                )
class IP():
    def __init__(self,ip):
        self.ip =ip
    def __str__(self):
        return "%d.%d.%d.%d" %(
                (self.ip & 0xff000000) >> 24,
                (self.ip & 0xff0000) >> 16,
                (self.ip & 0xff00) >> 8,
                self.ip & 0xff
                )

while True:
    packet = socket.recvfrom(4096)
    ethernet_header =struct.unpack("!6s6s2s", packet[0][0:14])
    final_size=14

    dst_ethernet_adder = ethernet_header[0].encode('hex')
    src_ethernet_adder = ethernet_header[1].encode('hex')
    protocol_type = "0x"+ethernet_header[2].encode('hex')


    print "=================================="
    print "Ethernet"
    print "=================================="
    print 
    print "Destination Mac Address  :  ",
    print Mac(dst_ethernet_adder)

    print "Source Macc Address  :  ",
    print Mac(src_ethernet_adder)
    print "Type : ",
    print protocol_type


    if protocol_type == "0x0806":
        arp_header=struct.unpack("!2s2s1s1s2s2s2s2s2s2s2s2s2s2s2s", packet[0][14:42])
        hardware_type = arp_header[0].encode('hex')
        protocol= arp_header[1].encode('hex')

        hardware_address_length= arp_header[2].encode('hex')
        protocol_address_length= arp_header[3].encode('hex')

        operation= arp_header[4].encode('hex')
        sha1= arp_header[5].encode('hex')
        sha2= arp_header[6].encode('hex')
        sha3= arp_header[7].encode('hex')

        spa1 = arp_header[8].encode('hex')
        spa2 = arp_header[9].encode('hex')

        tha1 = arp_header[10].encode('hex')
        tha2 = arp_header[11].encode('hex')
        tha3 = arp_header[12].encode('hex')

        tpa1 = arp_header[13].encode('hex')
        tpa2 = arp_header[14].encode('hex')
        print
        print

        print "=================================="
        print "Address Resolution Protocol"
        print "=================================="
        print
        print "Hardware Type : %d" %(int(hardware_type,16))
        print "Protocol Type : %d" %(int(protocol,16))
        print "Hardware Length : %d" %(int(hardware_address_length,16))
        print "Protocol Length : %d" %(int(protocol_address_length,16))
        print "Operation : %d" %(int(operation,16))
        print "Source Hardware address : ", Mac(sha1+sha2+sha3)
        print "Source Protocol address : ",IP(int(spa1+spa2,16))
        print "Destination HardWare address : ", Mac(tha1+tha2+tha3)
        print "Destination Protocol address : ", IP(int(tpa1+tpa2,16))
        print 
        final_size=42

    elif protocol_type == "0x0800":
        ip_header= struct.unpack("!1s1s2s2s2s1s1s2s4s4s",packet[0][14:34])
        version = int(ip_header[0].encode('hex'),16)  >> 4
        ihl= int(ip_header[0].encode('hex'),16)  & 0xf
        optional_size=0
        if ihl > 5:
            optional_size = (ihl<<2) - 20
        dscp = int(ip_header[1].encode('hex'),16) >> 2
        ecn= int(ip_header[1].encode('hex'),16) & 0x3
        
        total_length = int(ip_header[2].encode('hex'),16)
        identification = int(ip_header[3].encode('hex'),16)
        flags = int(ip_header[4].encode('hex'),16) >> 13
        flagement_offset = int(ip_header[4].encode('hex'),16) & 0x1fff
        ttl = int(ip_header[5].encode('hex'),16)
        protocol = int(ip_header[6].encode('hex'),16) 
        header_checksum = int(ip_header[7].encode('hex'),16)
        source_ip = int(ip_header[8].encode('hex'),16)
        dst_ip= int(ip_header[9].encode('hex'),16)
            
        print "=================================="
        print "Internet Protocol"
        print "=================================="
        print
        print "Version : ", version
        print "IHL : ",ihl << 2
        print "Service Type : ", dscp
        print "Total Legnth : %d" %(total_length)
        print "identification : %d" %(identification)
        print "flags : " , flags
        print "Reserved bit : ", (flags & 0x4 ) >>2
        print "Don't Fragment : ", (flags & 0x2) >> 1
        print "More Fragment : ", flags & 0x1
        print "Fragmentation offset : ", flagement_offset
        print "Time-to-live : ", ttl
        print "Protocol : ", protocol
        print "Header Checksum : ", header_checksum
        print "Source IP address : ", IP(source_ip)
        print "Destination IP address : ", IP(dst_ip)
        final_size=34
        if optional_size != 0:
            pre_size = 34
            final_size = optional_size+pre_size
            ip_header_option= struct.unpack("!"+str(optional_size)+"s",packet[0][pre_size:final_size])
            optional =int(ip_header_option[0].encode('hex'),16) 
            print "Option  : 0x%X" %(int(optional,16))
        

    if protocol == 6:
        tcp_header =struct.unpack("!2s2s4s4s1s1s2s2s2s", packet[0][final_size:final_size+20])

        print "=================================="
        print "Transport Control Protocol"
        print "=================================="
        
        src_port = tcp_header[0].encode('hex') 
        dst_port = tcp_header[1].encode('hex') 
        seq_num= tcp_header[2].encode('hex') 
        ack_num = tcp_header[3].encode('hex') 
        data_offset = int(tcp_header[4].encode('hex'),16) >> 4
        optional_size=0
        if data_offset > 5:
            optional_size = (data_offset<<2) - 20
        reserved = int(tcp_header[4].encode('hex'),16) & 0xe >> 1
        ns= int(tcp_header[4].encode('hex'),16) & 0x1
        cwr= int(tcp_header[5].encode('hex'),16) & 0x80 >> 7
        ece= int(tcp_header[5].encode('hex'),16) & 0x40 >> 6
        urg= int(tcp_header[5].encode('hex'),16) & 0x20 >> 5
        ack= int(tcp_header[5].encode('hex'),16) & 0x10 >> 4
        psh= int(tcp_header[5].encode('hex'),16) & 0x8 >> 3
        rst= int(tcp_header[5].encode('hex'),16) & 0x4 >> 2
        syn= int(tcp_header[5].encode('hex'),16) & 0x2 >> 1
        fin= int(tcp_header[5].encode('hex'),16) & 0x1
        window_size= tcp_header[6].encode('hex')
        checksum= tcp_header[7].encode('hex') 
        urg_pointer= tcp_header[8].encode('hex') 
        
        print "Source Port address : %d" %(int(src_port,16))
        print "Destination Port address : %d" %(int(dst_port ,16))
        print "Sequence Number : %d" %(int(seq_num ,16))
        print "Acknowlegement Number : %d" %(int(ack_num,16))
        print "Header Length : %d" %(data_offset << 2)
        print "Reserved : %d" %(reserved)
        print "URG : %d" %( urg )
        print "ACK : %d" %( ack )
        print "PSH : %d" %( psh )
        print "RST : %d" %( rst )
        print "SYN : %d" %( syn )
        print "FIN : %d" %( fin )
        print "Window size : %d" %(int(window_size,16))
        print "Checksum : 0x" + checksum 
        print "Urgent Pointer : %d" %(int(urg_pointer,16))
        if optional_size != 0:
            pre_size = final_size+20
            final_size = pre_size+optional_size
            tcp_header_option= struct.unpack("!"+str(optional_size)+"s",packet[0][pre_size:final_size])
            optional =tcp_header_option[0].encode('hex')
            print "Option  : 0x%X" %(int(optional,16))
    elif protocol == 17:
        udp_header =struct.unpack("!2s2s2s2s", packet[0][final_size:final_size+8])
        src_port=udp_header[0].encode('hex')
        dst_port=udp_header[0].encode('hex')
        length  =udp_header[0].encode('hex')
        checksum=udp_header[0].encode('hex')
        print "=================================="
        print "User Datagram Protocol"
        print "=================================="
        print
        print "Source Port : %d" %(int(src_port,16))
        print "Dst Port : %d" %(int(dst_port, 16))
        print "Length : %d"  %(int(length,16))
        print "Checksum: 0x%X"  %(int(checksum,16) )

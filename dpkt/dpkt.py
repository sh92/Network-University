#!/usr/bin/env python
"""
Use DPKT to read in a pcap file and print out the contents of the packets
This example is focused on the fields in the Ethernet Frame and IP packet
"""
import dpkt
import datetime
import socket


def mac_addr(address):
    """Convert a MAC address to a readable/printable string

       Args:
           address (str): a MAC address in hex form (e.g. '\x01\x02\x03\x04\x05\x06')
       Returns:
           str: Printable/readable MAC address
    """
    return ':'.join('%02x' % ord(b) for b in address)



def ip_to_str(address):
    """Print out an IP address given a string

    Args:
        address (inet struct): inet network address
    Returns:
        str: Printable/readable IP address
    """
    return socket.inet_ntop(socket.AF_INET, address)


def print_ip(pcap):
    ip = pcap.data

    do_not_fragment = bool(ip.off & dpkt.ip.IP_DF)
    more_fragments = bool(ip.off & dpkt.ip.IP_MF)
    fragment_offset = ip.off & dpkt.ip.IP_OFFMASK

    # Print out the info
    print 'IP: %s -> %s   (len=%d ttl=%d DF=%d MF=%d offset=%d)\n' % \
          (ip_to_str(ip.src), ip_to_str(ip.dst), ip.len, ip.ttl, do_not_fragment, more_fragments, fragment_offset)


def print_arp(pcap):

    arp = pcap.data

    hardware_type = arp.hrd
    protocol_type = arp.pro
    hardware_length = arp.hln
    protocol_length = arp.pln
    operation = arp.op
    sender_hardware_address = arp.sha
    sender_protocol_address = arp.spa
    target_hardware_address = arp.tha
    target_protocol_address = arp.tpa

    print 'Hardware type : ', hardware_type
    print 'Protocol type : ', protocol_type
    print 'Hardware length : ', hardware_length
    print 'Protocol length : ', protocol_length
    print 'Operation : ', operation
    print 'Sender Hardware Address : ', mac_addr(sender_hardware_address)
    print 'Sender Protocol Address : ', ip_to_str(sender_protocol_address)
    print 'Target Hardware Address : ', mac_addr(target_hardware_address)
    print 'Target Protocol Address : ', ip_to_str(target_protocol_address)

    print ''

def print_packets(pcap):
    """Print out information about each packet in a pcap

       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader)
    """
    # For each packet in the pcap process the contents
    for timestamp, buf in pcap:

        # Print out the timestamp in UTC
        print 'Timestamp: ', str(datetime.datetime.utcfromtimestamp(timestamp))

        # Unpack the Ethernet frame (mac src/dst, ethertype)
        eth = dpkt.ethernet.Ethernet(buf)
        print 'Ethernet Frame: ', mac_addr(eth.src), mac_addr(eth.dst), eth.type

        # Make sure the Ethernet frame contains an IP packet
        # EtherType (IP, ARP, PPPoE, IP6... see http://en.wikipedia.org/wiki/EtherType)
        if eth.type == dpkt.ethernet.ETH_TYPE_IP:
            print_ip(eth)

        elif eth.type == dpkt.ethernet.ETH_TYPE_ARP:
            print_arp(eth)

        else:
            print 'Non IP Packet type not supported %s\n' % eth.data.__class__.__name__
            continue

        # Now unpack the data within the Ethernet frame (the IP packet)
        # Pulling out src, dst, length, fragment info, TTL, and Protocol



def test():
    """Open up a test pcap file and print out the packets"""
    with open('sample.pcap') as f:
        pcap = dpkt.pcap.Reader(f)
        print_packets(pcap)



if __name__ == '__main__':
    test()

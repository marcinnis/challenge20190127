#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 21:07:15 2019

@author: nichu
"""

import socket
import threading
import socketserver
import struct
import ssl
import argparse

class BaseRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print("\nIncoming %s request" % (self.__class__.__name__[:3]))
        
        try:
            sock = self.connect_to_remote_dns()
            data = self.get_data()
            pack_length, result = self.send_dns_query(sock, data)
            self.send_data(result, pack_length)

        except Exception as e:
            print("Problem executing query: ", e)

    def send_dns_query(self,sock,dns_query):

        print("Connected to remote server. Protocol: ", sock.version())
        full_msg = struct.pack("!h", len(dns_query))
        full_msg += dns_query
        sock.send(full_msg)

        pack_length = sock.recv(2)
        msg_length, = struct.unpack('!h', pack_length)
        print('Received DNS packet with length: ', msg_length)
        return pack_length, sock.recv(msg_length)

    def connect_to_remote_dns(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(100)

        context = ssl.create_default_context()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_verify_locations('./ca-certificates.crt')

        finalsock = context.wrap_socket(sock, server_hostname=options.dnsip)
        finalsock.connect((options.dnsip, options.dnsport))

        return finalsock


class TCPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request.recv(4096)[2:]

    def send_data(self, data, pack_length):
        return self.request.sendall(pack_length + data)

class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0]

    def send_data(self, data, pack_length):
        return self.request[1].sendto(data, self.client_address)

# DNS-over-TLS info
#DNS_IP, DNS_PORT = '1.0.0.1', 853
# local instance info
LOCAL_IP = "0.0.0.0"

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='DNS over TLS implementation')
    parser.add_argument('-i', '--dns-ip', metavar='<server-ip>', type=str, dest='dnsip', required=True,
                        help='Remote DNS-over-TLS server IP address')
    parser.add_argument('-p', '--dns-port', metavar='<server-port>', type=int, dest='dnsport', required=True,
                        help='Remote DNS-over-TLS server IP address')    
    parser.add_argument('-l', '--local-port', metavar='<local-port>', type=int, default='53', dest='localport',
                        help='Local port for DNS queries listener')
    options = parser.parse_args()
     
    if options.dnsip and options.dnsport:
        servers = [
            socketserver.ThreadingUDPServer((LOCAL_IP, options.localport), UDPRequestHandler),
            socketserver.ThreadingTCPServer((LOCAL_IP, options.localport), TCPRequestHandler),
        ]
    
        for srv in servers:
            thread = threading.Thread(target=srv.serve_forever)
            thread.daemon = True
            thread.start()
            print("Starting %s thread of DNS-over-TLS server" % thread.name)
    
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
        finally:
            for s in servers:
                s.shutdown()

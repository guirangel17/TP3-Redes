#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import struct

'''
Formato do quadro:
TYP TTL IP PORT SQN TXT 
2   2   4    2   4
'''

#[18:53, 7/4/2017] Lucas Henrique: So usei B pros dados
#[18:54, 7/4/2017] Lucas Henrique: >H pra onde ta _16t na descricao
#[18:54, 7/4/2017] Lucas Henrique: e >I pra onde ta 32
#[18:54, 7/4/2017] Lucas Henrique: pros dados digo a key


def make_pkt(typ, ttl, ip, port, sqn, txt):
    TYP = struct.pack('>H', typ)
    TTL = struct.pack('>H', ttl)
    IP = struct.pack('=4sl', socket.inet_aton(ip), socket.INADDR_ANY)
    PORT = struct.pack('>H', port)
    SQN = struct.pack('>I', sqn)
    txt = map(lambda x: ord(x), txt)
    txt = struct.pack('%dB' % len(txt), *txt)

    pkt = TYP + TTL + IP + PORT + SQN + txt

    return pkt

def client():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 10000)

    msg = raw_input("digita uma mensagem: ")

    message = make_pkt(305, 25678, "192.168.1.1", 8000, 2, msg)

    try:
        # Send data
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)

        # Receive response
       # print >>sys.stderr, 'waiting to receive'
       # data, server = sock.recvfrom(4096)
       # print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

if __name__ == "__main__":
    sys.exit(client())

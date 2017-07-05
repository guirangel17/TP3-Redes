#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Programa cliente, que receberá do usuário chaves que devem ser consultadas e exibirá os resultados recebidos
import socket
import sys
import struct

'''
Formato do quadro:
TYP TTL IP PORT SQN TXT 
2   2   4    2   4
'''


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

    if len(sys.argv) < 2:
        print 'Execution format: $ python client.py [IP:port]'
        sys.exit()

    IP_PORT = sys.argv[1]
    IP = IP_PORT.split(":")[0]
    PORT = IP_PORT.split(":")[1]
    
    PORT = int(PORT)
    print PORT
   
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', PORT)

    msg = raw_input("Digite uma chave: ")

    message = make_pkt(1, 25678, IP, PORT, 2, msg)

    try:
        # Send data
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)

        # Aguarda 4 segundos uma respota
        # Se receber uma respota, entra em loop até aguardar 4 segundos sem receber nada novo
        # Exibe respostas ao usuário

        # sock.rcvfrom()
        # sock.settimeout(4seg)
        # if (sock.recvfrom) ----> irá retornar erro caso não seja recebido em 4seg, tem que tratar
        #       while (data) & timeout < 4seg
        #           print data

        

        # Receive response
        # print >>sys.stderr, 'waiting to receive'
        # data, server = sock.recvfrom(4096)
        # print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

if __name__ == "__main__":
    sys.exit(client())

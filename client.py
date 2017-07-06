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

def make_pkt_client(typ, txt):
    TYP = struct.pack('>H', typ)
    txt = map(lambda x: ord(x), txt)
    txt = struct.pack('%dB' % len(txt), *txt)

    pkt = TYP + txt
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
    message = make_pkt_client(1, msg)

    at_least_one_answer = False

    try:
        # Send data
        print >>sys.stderr, 'sending "%s"' % message

        try:
            # Envia mensagem ao seu servidor associado
            sent = sock.sendto(message, server_address)
            sock.settimeout(4.0)

            while(1):
                # Resposta de um servidor
                data, address_server = sock.recvfrom(100)
                TYP = struct.unpack(">H", data[0:2])[0]
                TXT = data[2:]
                print "\nServent: " + address_server[0] + ":" + str(address_server[1]) + " responded: \nkey\tvalue"
                print "---\t-----"
                print TXT
                at_least_one_answer = True

        except socket.timeout:
            # Esperou por 4 segundos e nao obteve nenhuma resposta
            if (at_least_one_answer == False):
                print "First Timeout. Resending"
                try:
                    # Envia mensagem ao seu servidor associado
                    sent = sock.sendto(message, server_address)
                    sock.settimeout(4.0)

                    # Resposta de um servidor
                    while (1):
                        # Resposta de um servidor
                        data, address_server = sock.recvfrom(100)
                        TYP = struct.unpack(">H", data[0:2])[0]
                        TXT = data[2:]
                        print "\nServent: " + address_server[0] + ":" + str(address_server[1]) + " responded: \nkey\tvalue"
                        print "---\t-----"
                        print TXT

                except socket.timeout:
                    print "Second Timeout! Key not found"

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

if __name__ == "__main__":
    sys.exit(client())

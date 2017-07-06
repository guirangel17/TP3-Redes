#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Programa servent, responsavel pelo armazenamento da base de dados chave-valor e pelo controle da troca de mensagem com seus pares.

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

def make_pkt_client(typ, txt):
    TYP = struct.pack('>H', typ)
    txt = map(lambda x: ord(x), txt)
    txt = struct.pack('%dB' % len(txt), *txt)

    pkt = TYP + txt
    return pkt

# Cria o dicionario de chave-valor passado no arquivo como parametro
def read_file(file_name):
    try:
        f = open(file_name, "r")
    except:
        print "Problem to open the file"

    dictionary = {}
    for line in f:
        if (str.strip(line[0]) != '#'):
            words = line.split()
            key = str.strip(words[0])
            text = words[1:]
            values = ' '.join(text)
            dictionary.update({key:values})

    return dictionary

def servent():
    num_params = len(sys.argv)
    
    if num_params < 3:
        print 'Execution format: $ python servent.py [localport] [key-values] [ip1:port1] ... [ipN:PortN]'
        sys.exit()

    LOCALPORT = int(sys.argv[1])
    key_values_file = sys.argv[2]

    neighbors = list()
    for i in range(3, num_params):
        neighbors.append(sys.argv[i])
    
    key_values = {}
    key_values = read_file(key_values_file)
           
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', LOCALPORT)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    print >> sys.stderr, '\nwaiting to receive message'

    sqn = 0 #sequence number

    # Message types
    # 1 - CLIREQ
    # 2 - QUERY
    # 3 - RESPONSE

    while (1): 
        data, address_client = sock.recvfrom(250)
        TYP = struct.unpack(">H", data[0:2])[0]

        if(TYP == 1): #mensagem vinda do client
            TXT = data[2:] #chave que está procurando
            TTL = 3

            # Enviar a mnsg para todos os vizinhos
            for i in neighbors:
                IP_neighbor = i.split(":")[0]
                PORT_neighbor = int(i.split(":")[1])
                address_neighbor = (IP_neighbor,PORT_neighbor)

                QUERY = make_pkt(2, TTL, IP_neighbor, PORT_neighbor, sqn + 1, TXT)
                sock.sendto(QUERY, address_neighbor)
            
            if TXT in key_values.keys():
                # responder ao cliente que a chave foi encontrada
                R = (TXT + '\t' + '\0')
                RESPONSE = make_pkt_client(3, R)
                sock.sendto(RESPONSE, address_client)

        #mensagem vinda de outro servent    
        elif (TYP == 2):
            TTL = struct.unpack(">H", data[2:4])[0]
            IP = socket.inet_ntoa(struct.unpack("=4sl", data[4:12])[0])
            PORT = struct.unpack(">H", data[12:14])[0]
            SQN = struct.unpack(">I", data[14:18])[0]
            TXT = data[18:]

            # Alagamento confiavel OSPF
            # if mensagem nao foi recebida anteriormente:
            #       if TXT in key_values.keys():
            #           # responder ao cliente que a chave foi encontrada
            #            R = (TXT + '\t' + '\0')
            #            RESPONSE = make_pkt_client(3, R)
            #            sock.sendto(RESPONSE, address_client)
            #
            #       TTL = TTL - 1
            #       if TTL > 0:
            #           manda pros vizinho, menos aquele que chamou
            #           QUERY = make_pkt(TYP,TTL-1,IP,PORT,SQN,TXT)
            print ''

        # if data:
        #     sent = sock.sendto(data, address)
        #     print >> sys.stderr, 'sent %s bytes back to %s' % (sent, address)

if __name__ == "__main__":
    sys.exit(servent())

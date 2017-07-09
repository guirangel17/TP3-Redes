''' 
TP3 - Redes de Computadores - servent.py
 
Desenvolvido por:
     - Gabriela Brant Alves                2013062901
     - Guilherme Rangel da Silva Moura     2013062960
'''

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
    except (OSError, IOError) as e:
        print "Problem to open the file."

    dictionary = {}
    for line in f:
        words = line.split()
        if (words[0] != '#'): # primeira palavra da linha
            if (str.strip(words[0][0]) != '#'): # primeiro caracter da palavra
                key = str.strip(words[0])
                text = words[1:]
                values = ' '.join(text)
                dictionary.update({key:values})

    f.close()
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
    print 'Connection established at',server_address

    sock.bind(server_address)
    print '\nWaiting to receive message... \n'

    sqn = 0 #sequence number

    # Message types
    # 1 - CLIREQ
    # 2 - QUERY
    # 3 - RESPONSE
    msg_history = list()

    while (1):
        data, address = sock.recvfrom(250)
        TYP = struct.unpack(">H", data[0:2])[0]

        if(TYP == 1): # mensagem vinda do client
            sqn = sqn + 1
            address_client = address
            TXT = data[2:] # chave que esta procurando
            TTL = 3
            
            print '\nTYP = CLIREQ'
            print 'Client', address, 'is looking for key', 'TXT =', TXT

            # Enviar a mnsg para todos os vizinhos
            for i in neighbors:
                IP_neighbor = i.split(":")[0]
                PORT_neighbor = int(i.split(":")[1])
                address_neighbor = (IP_neighbor,PORT_neighbor)

                QUERY = make_pkt(2, TTL, address_client[0], address_client[1], sqn, TXT)
                sock.sendto(QUERY, address_neighbor)

            if TXT in key_values.keys():
                # responder ao cliente que a chave foi encontrada
                R = (TXT + '\t' + key_values[TXT] + '\0')
                RESPONSE = make_pkt_client(3, R)
                sock.sendto(RESPONSE, address_client)

        #mensagem vinda de outro servent    
        elif (TYP == 2):
            address_server_before = address

            TTL = struct.unpack(">H", data[2:4])[0]
            IP = socket.inet_ntoa(struct.unpack("=4sl", data[4:12])[0])
            PORT = struct.unpack(">H", data[12:14])[0]
            SQN = struct.unpack(">I", data[14:18])[0]
            TXT = data[18:]

            client_address = (IP,PORT)

            print '\nTYP = QUERY'
            print 'Message from servent', address, 'TTL =', TTL
            print 'Client', client_address, 'is looking for key', TXT

            # Se a mnsg n foi vista anteriormente, procurar chave
            received_msg = (IP, PORT, SQN, TXT)

            if (received_msg not in msg_history):
                msg_history.append(received_msg)

                # Alagamento confiavel OSPF
                if TXT in key_values.keys():
                    # responder ao cliente que a chave foi encontrada
                    R = (TXT + '\t' + key_values[TXT] + '\0')
                    RESPONSE = make_pkt_client(3, R)

                    sock.sendto(RESPONSE, client_address)

                TTL = TTL - 1
                if TTL > 0:
                    # Manda pros vizinhos, menos aquele que chamou
                    for i in neighbors:
                        IP_neighbor = i.split(":")[0]
                        PORT_neighbor = int(i.split(":")[1])
                        address_neighbor = (IP_neighbor, PORT_neighbor)

                        if address_neighbor != address_server_before: # Verificando o vizinho que chamou
                            QUERY = make_pkt(TYP, TTL, IP, PORT, SQN, TXT)
                            sock.sendto(QUERY, address_neighbor)

if __name__ == "__main__":
    sys.exit(servent())

#Programa servent, responsavel pelo armazenamento da base de dados chave-valor e pelo controle da troca de mensagem com seus pares.


import socket
import sys
import struct


'''
Formato do quadro:
TYP TTL IP PORT SQN TXT 
2   2   4    2   4
'''

def read_pkt (data):
    TYP = struct.unpack(">H", data[0:2])[0]
    TTL = struct.unpack(">H", data[2:4])[0]
    IP = socket.inet_ntoa(struct.unpack("=4sl", data[4:12])[0])
    PORT = struct.unpack(">H", data[12:14])[0]
    SQN = struct.unpack(">I", data[14:18])[0]
    TXT = data[18:]
    return TXT


def toString(data):
	return ''.join('%02X' % ord(x) for x in data)


def servant():
    num_params = len(sys.argv)
    
    if num_params < 3:
        print 'Execution format: $ python servent.py [localport] [key-values] [ip1:port1] ... [ipN:PortN]'
        sys.exit()

    LOCALPORT = int(sys.argv[1])
    key_values_file = sys.argv[2]
    
    PORT = list()
    for i in range(3, num_params):
        PORT.append(sys.argv[i])
        # criar lista IP:port

    f = open(key_values_file, "r")

    # Cria o dicionario de chave-valor passado no arquivo como parametro
    key_values = {}
    for line in f:
        if (line[0] != '#'):
            words = line.split()
            key = str.strip(words[0])
            text = words[1:]
            values = ' '.join(text)
            key_values.update({key:values})
            
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', LOCALPORT)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    print >> sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(250)

    dataTXT = read_pkt(data)

    print >> sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >> sys.stderr, data
    print dataTXT

    if data:
        sent = sock.sendto(data, address)
        print >> sys.stderr, 'sent %s bytes back to %s' % (sent, address)

if __name__ == "__main__":
    sys.exit(servant())

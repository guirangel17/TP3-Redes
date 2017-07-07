''' 
TP3 - Redes de Computadores - client.py
 
Desenvolvido por:
     - Gabriela Brant Alves                2013062901
     - Guilherme Rangel da Silva Moura     2013062960
'''

# Programa cliente, que recebera do usuario chaves que devem ser consultadas e exibira os resultados recebidos dos servents

import socket
import sys
import struct

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
    PORT = int(IP_PORT.split(":")[1])
    
   
    # Cria socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (IP, PORT)

    print 'Connection established at',server_address

    while(1):
        msg = raw_input("\n \nEnter a key: ")
        message = make_pkt_client(1, msg)

        at_least_one_answer = False

        try:
            # Envia mensagem ao seu servidor associado
            sent = sock.sendto(message, server_address)
            print 'Sending', msg
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

                    while (1):
                        # Resposta de um servidor
                        data, address_server = sock.recvfrom(100)
                        TYP = struct.unpack(">H", data[0:2])[0]
                        TXT = data[2:]
                        print "\nServent: " + address_server[0] + ":" + str(address_server[1]) + " responded: \nkey\tvalue"
                        print "---\t-----"
                        print TXT

                except socket.timeout:
                    print "Second Timeout! \nKEY NOT FOUND."

if __name__ == "__main__":
    sys.exit(client())

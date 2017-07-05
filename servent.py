import socket
import sys
import struct

'''
Formato do quadro:
TYP TTL IP PORT SQN TXT 
2   2   4    2   4
'''

def toString(data):
	return ''.join('%02X' % ord(x) for x in data)

def servant():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    print >> sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(250)

    TYP = struct.unpack(">H", data[0:2])[0]
    TTL = struct.unpack(">H", data[2:4])[0]
    IP = socket.inet_ntoa(struct.unpack("=4sl", data[4:12])[0])
    PORT = struct.unpack(">H", data[12:14])[0]
    SQN = struct.unpack(">I", data[14:18])[0]
    TXT = data[18:]

    print >> sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >> sys.stderr, data

    if data:
        sent = sock.sendto(data, address)
        print >> sys.stderr, 'sent %s bytes back to %s' % (sent, address)

if __name__ == "__main__":
    sys.exit(servant())

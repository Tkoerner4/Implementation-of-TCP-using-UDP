import socket
import random
import struct
# These functions will be used to simulate an unreliable channel
# that can corrupt a packet while receiving it
# or drop a packet while sending it

# If you want to no drops or corruption (while starting to write your code)
# use

probability = 1

# else it can be anything < 1, test your code for different values
def recv_packet(socket):
    received_data, recv_addr = socket.recvfrom(1472)
    seqnum = int.from_bytes(received_data[4:8], byteorder='big')
    #corrupt the packet
    if random.random()>probability and seqnum>0:
        print("Packet with seqnum:"+str(seqnum) + " is corrupted!")
        received_data+=b"corrupted!"
    
    return received_data,recv_addr


def send_packet(socket,packet,recv_addr):
    #drop the packet 5% of the time
    seqnum=int.from_bytes(packet[4:8], byteorder='big')
    if random.random()>probability and seqnum>0:
        print("Packet dropped with seqnum:"+str(seqnum))
    else:
        socket.sendto(packet,recv_addr)
    
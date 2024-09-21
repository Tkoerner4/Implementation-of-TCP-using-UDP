## The code provided here is just a skeleton that can help you get started
## You can add/remove functions as you wish

import threading
import zlib
import sys
import socket



from unreliable_channel import recv_packet, send_packet

def create_ack_packet(seq_num):
    
    type_bytes = b'\x00\x00\x00\x01'  # Assuming 1 represents ACK type
    
    #print("Sequence number is:"+str(seq_num))
    print("Creating ack packet for seq num:"+str(seq_num))
    seqnum_bytes = seq_num.to_bytes(4, byteorder='big')
    
    length_bytes = b'\x00\x00\x00\x10'  #16
    checksum = zlib.crc32(type_bytes + seqnum_bytes + length_bytes) & 0xffffffff
    checksum_bytes = checksum.to_bytes(4, byteorder='big')
    return type_bytes + seqnum_bytes + length_bytes + checksum_bytes,checksum


# create ack packet
# crc32 available through zlib library



def extract_packet_info(packet):
    
    seq_num = int.from_bytes(packet[4:8], byteorder='big')
    expected_length = int.from_bytes(packet[8:12], byteorder='big')
    received_checksum = int.from_bytes(packet[12:16], byteorder='big')
    data = packet[16:]
    calculated_checksum = zlib.crc32(packet[:12])
    if (expected_length != len(packet)) or (received_checksum != calculated_checksum):
        status = "CORRUPT"
    else:
        status = "NOT CORRUPT"
    
    return seq_num, status, data,expected_length,received_checksum,calculated_checksum



# extract the data packet after receiving


def receive_packets(sock, output_file, recv_log_file):
    last_correct_packet = 0
    expected_seq_num = 0  #
    with open(output_file, 'wb') as out_file, open(recv_log_file, 'w') as log_file:
        while True:  
            #--------------------------------------
            #packet, addr = sock.recvfrom(1472)
            packet, addr = recv_packet(sock)
            #--------------------------------------
            seq_num, status, data,length,received_checksum,calculated_checksum = extract_packet_info(packet)
            
            
            
            #Packet received; type=DATA; seqNum=0; length=1472; checksum_in_packet=62c0c6a2;checksum_calculated=62c0c6a2; status=NOT_CORRUPT
            log_file.write("Packet received; type=DATA; seqNum="+str(seq_num)+"; length="+str(length)+"; checksum_in_packet=" +hex(received_checksum) +"; checksum_calculated="+hex(calculated_checksum)+"; status="+status+"\n")
            print("Packet received; type=DATA; seqNum="+str(seq_num)+"; length="+str(length)+"; checksum_in_packet=" +hex(received_checksum) +"; checksum_calculated="+hex(calculated_checksum)+"; status="+status)
            if seq_num != expected_seq_num:# if out of order
                print("Packet "+str(seq_num)+" out of order, expected Packet "+str(expected_seq_num))
                log_file.write("Packet "+str(seq_num)+" out of order, expected Packet "+str(expected_seq_num)+"\n")
                
                ack_packet,_ = create_ack_packet(last_correct_packet)
            
            if seq_num == expected_seq_num and (status == "NOT CORRUPT"):#if packet is in order and not corrupt
                out_file.write(data) # add data to outfile
                last_correct_packet = seq_num # save it as last correct packet
                expected_seq_num += 1 #should be expecting the next seqnum packet
                ack_packet,checksum = create_ack_packet(expected_seq_num - 1)
                
            
                
            
            if status == "CORRUPT":#if corrupt
                print("Packet "+str(seq_num)+" is corrupt")
                log_file.write("Packet "+str(seq_num)+" is corrupt\n")
                ack_packet,_ = create_ack_packet(last_correct_packet)
                

                
            #ack_packet,checksum = create_ack_packet(expected_seq_num - 1)
            
            #--------------------------------------
            #sock.sendto(ack_packet, addr)
            send_packet(sock, ack_packet, addr)
            #--------------------------------------
            log_file.write("Packet sent; type=ACK; seqNum="+str(expected_seq_num - 1)+"; length=16; checksum_in_packet="+hex(checksum)+"\n")
            print("Packet sent; type=ACK; seqNum="+str(expected_seq_num - 1)+"; length=16; checksum_in_packet="+hex(checksum))
            if(len(data) < 1456):
                print("Last Ack sent")
                log_file.write("Last Ack sent\n")
                break

if len(sys.argv) != 4:
    print("Usage: python mtpReceiver.py <receiver-port> <output-file> <receiver-log-file>")
    sys.exit(1)

recv_port=int(sys.argv[1])
output_file=sys.argv[2]
recv_log_file =sys.argv[3]

# socket 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('localhost', recv_port))


receive_packets(sock, output_file, recv_log_file)

# your main thread can act as the receive thread that receives DATA packets

	# while there packets being received:
		# receive packet, but using our unreliable channel
		# packet_from_sender, sender_addr = unreliable_channel.recv_packet(socket)
		# call extract_packet_info
		# check for corruption and lost packets, send ack accordingly
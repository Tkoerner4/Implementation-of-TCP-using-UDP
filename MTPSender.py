import threading
import zlib
import sys
import socket
import time
import struct
from unreliable_channel import recv_packet, send_packet
import random


#TODO MAKE SURE THE SEND_PACKET AND RECV_PACKET ARE CORRECT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
WE10022Count = 0
recvClosed = False
currSeqNum = 0

lock = threading.Lock()
pktList = []
ackReceived = threading.Event()
endOfFile = False
lastAckReceived = -1
dupAckCount = {}
senderLog = []
checksums = []
timesSent = {}

def create_packet(data, seqnum):
    
    typeBytes = b'\x00\x00\x00\x00'#bytes for data type
    seqnumBytes = seqnum.to_bytes(4, byteorder='big')
    lengthBytes = (len(data) + 16).to_bytes(4, byteorder='big')
    checksum = zlib.crc32(typeBytes + seqnumBytes + lengthBytes) & 0xffffffff
    checksums.append(checksum)
    
    checksumBytes = checksum.to_bytes(4, byteorder='big')
    return typeBytes + seqnumBytes + lengthBytes + checksumBytes + data
# create data packet
# crc32 available through zlib library
def send(ip, port):
    global currSeqNum, windowSize, endOfFile, lastAckReceived,sock,recvClosed
    
    while not endOfFile and currSeqNum > lastAckReceived:#while file is not done being sent, and packets are in order
        with lock:
            startSeqNum = currSeqNum#start window
            for i in range(startSeqNum, startSeqNum + windowSize): #for window size
                if i < len(pktList) and i >= currSeqNum:# If not at the end and in order
                    #---------------------------
                   
                    #sock.sendto(pktList[i], (ip, port))
                    send_packet(sock, pktList[i], (ip, port))
                    
                    
                    
                    #---------------------------
                    timesSent[i] = time.time()
                    senderLog.append("Packet sent;type = DATA; seqNum="+str(i)+"; length="+str(len(pktList[i]))+"; checksum="+hex(checksums[i])) 
                    print("Packet sent;type = DATA; seqNum="+str(i)+"; length="+str(len(pktList[i]))+"; checksum="+hex(checksums[i]))
                    #print("Sent packet "+str(pktList[i])) 
                    #senderLog.append("Sent packet "+str(pktList[i]))
                    if i == len(pktList) - 1:  # Last packet
                        endOfFile = True
                        print("Last packet sent")
                        senderLog.append("Last packet sent")
        if recvClosed == True:
            break               
        time.sleep(0.5)



def recv(receiverIp,receiverPort):
    global currSeqNum, lastAckReceived, dupAckCount, lock, ackReceived,sock,recvClosed,WE10022Count
    while True:
        try:
            #---------------------------
            #data, _ = sock.recvfrom(1472)
            data,_ = recv_packet(sock)
            
            #---------------------------
            if len(data) == 16:
                ack_type, ack_seqnum, length, checksum = struct.unpack('!4I', data)
                if ack_type == 1:
                    with lock:
                        if ack_seqnum == currSeqNum:
                            
                            calculated_checksum = zlib.crc32(data[:12]) & 0xffffffff
                            if calculated_checksum != checksum:
                                status = "CORRUPT"
                            else:  
                                status = "NOT CORRUPT"
                                
                            print("Packet received; type=ACK; seqNum="+str(ack_seqnum)+"; length=16; checksum_in_packet="+hex(checksum)+"; calculated_checksumn="+hex(calculated_checksum)+"; status="+status)
                            senderLog.append("Packet received; type=ACK; seqNum="+str(ack_seqnum)+"; length=16; checksum_in_packet="+hex(checksum)+"; calculated_checksumn="+hex(calculated_checksum)+"; status="+status)
                            currSeqNum += 1
                            ackReceived.set() #ack received
                            lastAckReceived = ack_seqnum
                            dupAckCount[ack_seqnum] = 0  # Reset
                            if abs(time.time() - timesSent[ack_seqnum])  > 0.5:
                                print("Timeout; seqNum="+str(ack_seqnum))
                                senderLog.append("Timeout; seqNum="+str(ack_seqnum))
                                send_packet(sock,pktList[lastAckReceived], (receiverIp, receiverPort))
                                time.sleep(0.5)
                                #[WinError 10054] An existing connection was forcibly closed by the remote host
                            
                        elif ack_seqnum < currSeqNum:
                            if ack_seqnum not in dupAckCount.keys():
                                dupAckCount[ack_seqnum] = 1
                                print("Duplicate ACK received; seqNum="+str(ack_seqnum)+"; count="+str(dupAckCount[ack_seqnum]))
                                print("Expected ack for packet: "+str(currSeqNum))
                                senderLog.append("Duplicate ACK received; seqNum="+str(ack_seqnum)+"; count="+str(dupAckCount[ack_seqnum]))
                            else:  
                                dupAckCount[ack_seqnum] += 1
                                print("Duplicate ACK received; seqNum="+str(ack_seqnum)+"; count="+str(dupAckCount[ack_seqnum]))
                                print("Expected ack for packet: "+str(currSeqNum))
                                senderLog.append("Duplicate ACK received; seqNum="+str(ack_seqnum)+"; count="+str(dupAckCount[ack_seqnum]))
                            if dupAckCount[ack_seqnum] == 3:  # if third ack reiccve for current seqnum pakcet
                                senderLog.append("Triple duplicate ACKs received; seqNum="+str(ack_seqnum)+"; Retransmit")
                                print("Triple duplicate ACKs received; seqNum="+str(ack_seqnum)+"; Retransmit")
                                #---------------------------
                                #sock.sendto(pktList[ack_seqnum], (receiverIp, receiverPort))
                                send_packet(sock,pktList[lastAckReceived], (receiverIp, receiverPort))
                                time.sleep(0.5)
                                #---------------------------
                                
                                dupAckCount[ack_seqnum] = 0  # reset ack counter
                                
                        if(ack_seqnum == len(pktList)-1):
                            print("Last ACK received")
                            senderLog.append("Last ACK received")
                            break
        except KeyboardInterrupt:
            print("Interrupted by user. Exiting...")
            break
        except Exception as e:
            print("Error receiving ACK: "+str(e))
            if e.errno == 10022:
                WE10022Count += 1
                if WE10022Count == 50:
                    break
            if e.errno == 10054:
                print("Connection closed by remote host")
                recvClosed = True
                break


            
# receive ack, but using our unreliable channel
		# packet_from_receiver, receiver_addr = unreliable_channel.recv_packet(socket)
		# call extract_packet_info
		# check for corruption, take steps accordingly
		# update window size, timer, triple dup acks

if len(sys.argv) == 5:
    receiverIp=sys.argv[0]
    receiverPort = int(sys.argv[1])
    windowSize = int(sys.argv[2])
    inputFile=sys.argv[3]
    senderLogFile = sys.argv[4]

if len(sys.argv) == 6:
    receiverIp=sys.argv[1]
    receiverPort = int(sys.argv[2])
    windowSize = int(sys.argv[3])
    inputFile=sys.argv[4]
    senderLogFile = sys.argv[5]
if (len(sys.argv) != 6) and (len(sys.argv) != 5):        
    print("Usage: python mtpSender.py <receiver-IP> <receiver-port> <window-size> <input-file> <sender-log-file>")
    sys.exit(1)


"""
receiverIp = "localhost"
receiverPort=12345
windowSize=5
inputFile="t1.txt"
senderLogFile="senderLog.txt"
"""

with open(inputFile, "rb") as file:
    fileBytes = file.read()
    for i in range(0, len(fileBytes), 1456):
        pktList.append(create_packet(fileBytes[i:i + 1456], i // (1456)))
    
    
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM

    
   

recv_thread = threading.Thread(target=recv, args=(receiverIp,receiverPort))
send_thread = threading.Thread(target=send, args=(receiverIp,receiverPort))
#starting thredas
recv_thread.start()
send_thread.start()

#waiting for them to end
send_thread.join()
recv_thread.join()

   

print("Length of sender log: ", len(senderLog))
# putting contents of senderlog into the file 
with open(senderLogFile, "w") as logFile:
    for entry in senderLog:
        logFile.write(entry + "\n")
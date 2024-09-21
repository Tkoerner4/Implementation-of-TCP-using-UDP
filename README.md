# Implementation-of-TCP-using-UDP

This repository contains an implementation of TCP using UDP. It ensures reliable file transfer between two machines by handling packet loss and corruption. There is a sender and receiver program, where the sender transmits a file over UDP, and the receiver verifies its integrity upon completion

# Usage
To compile and run this program, you need to be in the same directory as Receiver.py, Sender.py, and unreliable_channel.py
using the commands: 
python Receiver.py 12345 received_file.txt receiver_log.txt
and
python Sender.py localhost 12345 50 1MB.txt sender_log.txt

1MB is just a sample of data to send over the connection, you can send any .txt file

In the Sender and Receiver files, the send methods are from unreliable channel. The normal equivalent is below them so if you want to use the normal method
just comment out the line with the method from unreliable_channel and uncomment the line with the normal methods.

Running the files with 
.\Sender.py localhost 12345 50 1MB.txt sender_log.txt 
and
.\Receiver 12345 received_file.txt receiver_log.txt
 may cause issues sometimes, as I've seen in my testing.

However, running
 .\Sender.py localhost 12345 50 1MB.txt sender_log.txt
and 
python Receiver.py 12345 received_file.txt receiver_log.txt
Did not seem to cause any errors.

# Specifications
There are only 2 packet types, DATA packets, which contain the data of the sent file, and ACK packets. The sender sends the DATA packets and
when the receiver receives them, ACK packets are sent back. Since this is a reliable delivery protocol,
the DATA packets and ACKs should contain a sequence number

# Packet info
Each packet can be a max size of 1500 bytes. The first 8 bytes of each packet are the UDP heaader, the next 20 bytes are the IP header. The IP header contains 4 unsigned integers, one for type, 
signifying if this packet is a DATA or ACK packet, a sequence number to track order of packet transmission, length of the data + IP header, and a 4 byte CRC checksum

# Multithreading design
This design implements two threads (one for sending and another for receiving) on both
the sender and receiver.
- The send thread on the sender sends the DATA packets.
- The receive thread on the receiver receives the DATA packets.
- The send thread on the receiver sends the ACK packets.
- The receive thread on the sender receives the ACK packets.

# Reliable delivery policy


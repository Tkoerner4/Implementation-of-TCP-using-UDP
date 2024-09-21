# Implementation-of-TCP-using-UDP

This repository contains the implementation of the Mason Transport Protocol (MTP), a reliable transport protocol built over UDP. Unlike standard TCP, MTP ensures reliable file transfer between two machines by handling packet loss and corruption. The project includes a sender and receiver program, where the sender transmits a file over UDP, and the receiver verifies its integrity upon completion

# Usage
To compile and run this program, you need to be in the same directory as MTPReceiver.py, MTPSender.py, and unreliable_channel.py
using the commands: 
python MTPReceiver.py 12345 received_file.txt receiver_log.txt
and
python MTPSender.py localhost 12345 50 1MB.txt sender_log.txt

1MB is just a sample of data to send over the connection, you can send any .txt file

In the MTPSender and MTPReceiver files, the send methods are from unreliable channel. The normal equivalent is below them so if you want to use the normal method
just comment out the line with the method from unreliable_channel and uncomment the line with the normal methods.

Running the files with 
.\MTPSender.py localhost 12345 50 1MB.txt sender_log.txt 
and
.\MTPReceiver 12345 received_file.txt receiver_log.txt
 may cause issues sometimes, as I've seen in my testing.

However, running
 .\MTPSender.py localhost 12345 50 1MB.txt sender_log.txt
and 
python MTPReceiver.py 12345 received_file.txt receiver_log.txt
Did not seem to cause any errors.

import random
import socket
import struct
import hashlib
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
unpacker = struct.Struct('I I 8s 32s')

#Create the socket and listen
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

sequenceNumExpected = 0

# Send packet function to return packets back to the client
def sendPacket(ack, UDP_Packet, chksum):
    sendValues = (ack, sequenceNumExpected, UDP_Packet[2], chksum)
    UDP_Packet_Data = struct.Struct('I I 8s 32s')
    UDP_Packet = UDP_Packet_Data.pack(*sendValues)
    sock.sendto(UDP_Packet, (UDP_IP, 4004))

# 50% chance that the packet is lost, so we will skip the rest of the code
    # and continue the while loop, the client will time out and resent the packet
def lostPacket():
    v = random.choice([0, 1, 1, 0])
    if v == 1:
        print('Packet lost')
    return v

# 33% of packets are delayed
def delayedPacket():
    v = random.choice([0, 1, 0])
    if v == 1:
        time.sleep(0.1)
        print('Packet Delayed')

# 50% of packets are corrupt, if corrupt set the check sum to corrupt
def packetCorrupt(UDP_Packet):
    if random.choice([0,1,0,1]) == 1:
        checkSum = b'Corrupt'
        print('Packet checksum corrupted')
        sendPacket(0, UDP_Packet, checkSum)


while True:
    #Receive Data
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    UDP_Packet = unpacker.unpack(data)

    # Check is packet is lost
    if lostPacket() == 1:
        continue

    print("received packet:", UDP_Packet)

    #Create the Checksum for comparison
    values = (UDP_Packet[0],UDP_Packet[1],UDP_Packet[2])
    packer = struct.Struct('I I 8s')
    packed_data = packer.pack(*values)
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

    # Check if packet is delayed
    delayedPacket()

    # Check if packet is corrupted
    packetCorrupt(UDP_Packet)

    #Compare Checksums to test for corrupt data
    if UDP_Packet[3] == chksum:
        print('CheckSums Match, Packet OK')
        sendPacket(1, UDP_Packet, chksum)
        print('Packet acked and returned to client')

        # Change expected sequence number for next packet
        if sequenceNumExpected == 0:
            sequenceNumExpected = 1
        else:
            sequenceNumExpected = 0
    else:
        print('Checksums Do Not Match, Packet Corrupt')
import socket
import struct
import hashlib

# UDP identification
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("")

# Array of packet data
pkt_data = ["NCC-1701", "NCC-1422", "NCC-1017"]

# Socket setup
sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, 4004))  # Listen to socket on this port

# Send a packet
def sendPacket(pktdata, sequenceNum):
    # Create the Checksum
    b = bytes(pktdata, encoding='utf-8')
    values = (0, sequenceNum, b)
    UDP_Data = struct.Struct('I I 8s')
    packed_data = UDP_Data.pack(*values)
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

    # Build the UDP Packet
    values = (0, sequenceNum, b, chksum)
    UDP_Packet_Data = struct.Struct('I I 8s 32s')
    UDP_Packet = UDP_Packet_Data.pack(*values)

    # Send the UDP Packet
    while True:
        try:
            sock.sendto(UDP_Packet, (UDP_IP, UDP_PORT))
            print('packet sent from client', values)
            # Receive packet
            unpacker = struct.Struct('I I 8s 32s')
            # Set the time out time
            sock.settimeout(0.009)
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            UDP_Packet1 = unpacker.unpack(data)
            # If packet is ACKed then client has received the packet
            if (UDP_Packet1[0] == 1) & (UDP_Packet1[3] == chksum):
                print("received non-corrupt, acked packet from server:", UDP_Packet1)
                break
            # If checksum is not the same, then packet is corrupted
            if UDP_Packet1[3] != chksum:
                print("packet corrupted, resending packet")
                continue
        # Resend packet if socket times out
        except socket.timeout:
            print('socket timeout, resending packet')
            continue


sequenceNum = 0

# Iterate through packet data array and send all packets
# Change sequence number (0 to 1 and vice versa) for each packet
for x in pkt_data:
    sendPacket(x, sequenceNum)
    if sequenceNum == 0:
        sequenceNum = 1
    else:
        sequenceNum = 0

# Close socket after all packets have been sent
sock.close()

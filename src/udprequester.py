import random
import struct
import socket
from numpy import uint64, uint32, iinfo


class udpScraper:
    def __init__(self, trackerAddress:tuple, info:bytes):
        self.iHash = info
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.trackerAddress = trackerAddress
        try:
            self.protocolID = uint64(0x41727101980)
            self.action = uint32(0) #uint32(iinfo(uint32).max - 1)
            self.transactionID = self.getRandom32() #uint32(iinfo(uint32).max)
            self.connnectionID = uint32(0) #uint32(iinfo(uint32).max)
        except OverflowError:
            print("[UDPRequester __init__]: \033[41mError:\033[0m Packet variable out of bounds for uint32")
            return


    def getRandom32(self):
        return uint32(random.randint(1, iinfo(uint32).max))

    def getConnectRequestPacket(self):
        self.action = uint32(0)
        #Combine action (uint32) and transaction ID (uint32) into a uint64
        combined = uint64(self.action)
        combined = combined << 32
        combined = combined | self.transactionID


        packet = struct.pack(">QQ", self.protocolID, combined)
        conv = "0x" + str(packet.hex())
        # print(conv)
        # print("\n\n")
        # print(bin(int(conv, 16)))
        return packet

    def getScrapeRequestPacket(self):
        self.action = 2
        #self.transactionID = self.getRandom32()

        combined = uint64(self.action)
        combined = combined << 32
        combined = combined | self.transactionID

        packet = struct.pack(">QQ20s", self.connnectionID, combined, self.iHash)
        conv = "0x" + str(packet.hex())
        # print(conv)
        # print("\n\n")
        # print(bin(int(conv, 16)))
        return packet

    def sendRequest(self, request:bytes):
        self.socket.sendto(request, self.trackerAddress)

    def listen(self):
        resp, addr = self.socket.recvfrom(4096)
        self.socket.close()
        # print(resp)
        return resp




if __name__ == "__main__":
    r = udpScraper((socket.gethostbyname("tracker.opentrackr.org"), 1337), None)
    connPack = r.getConnectRequestPacket()
    r.sendRequest(connPack)
    resp = r.listen()
    print(bin(int("0x" + str(resp.hex()), 16)))
    unpacked = struct.unpack(">QQ", resp)
    print(bin(unpacked[0]))
    print(bin(unpacked[1]))
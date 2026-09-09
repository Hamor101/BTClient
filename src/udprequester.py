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

    def decodeConnectResponsePacket(self, responsePacket):
        out = struct.unpack(">QQ", responsePacket)
        print(out)
        # print(bin(tId))
        # print(bin(conn_id))


    def sendRequest(self, request:bytes):
        self.socket.sendto(request, self.trackerAddress)

    def listen(self):
        resp, addr = self.socket.recvfrom(4096)
        self.socket.close()
        # print(resp)
        return resp

    def hexToBinaryLossless(self, hxBytes:bytes):
        hxBytes = str(hxBytes.hex())
        res = ""
        for i in hxBytes:
            convVal = bin(int(i, 16))[2::]
            # Pad the individual character values with leading zeroes if they get cut off by the binary conversion
            if len(convVal) < 4:
                convVal = "0"*(4-len(convVal)) + convVal
            res += convVal
        return res


if __name__ == "__main__":
    r = udpScraper((socket.gethostbyname("tracker.opentrackr.org"), 1337), None)

    # connPack = r.getConnectRequestPacket()
    # r.sendRequest(connPack)
    # resp = r.listen()

    tId = 0
    # print(bin(r.transactionID))
    with open("connect_response.bin", "rb") as f:
        resp = f.read()
    with open("transactionIdTemp.txt", "r") as f:
        tId = f.read()
    print(resp.hex())
    print(tId)
    print(r.hexToBinaryLossless(resp))
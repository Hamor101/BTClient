import random
import struct
from numpy import uint64, uint32, iinfo


class udpScraper:
    def __init__(self, info):
        try:
            self.protocolID = uint64(0x41727101980)
            self.action = uint32(0) #uint32(iinfo(uint32).max - 1)
            self.transactionID = uint32(iinfo(uint32).max) #self.getRandom32()
            self.connnectionID = uint32(iinfo(uint32).max) # uint32()
            self.iHash = info
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
        print(conv)
        print(bin(int(conv, 16)))
        return packet

    def getScrapeRequestPacket(self):
        self.action = 2
        #self.transactionID = self.getRandom32()

        combined = uint64(self.action)
        combined = combined << 32
        combined = combined | self.transactionID

        packet = struct.pack(">QQ20s", self.connnectionID, combined, self.iHash)
        conv = "0x" + str(packet.hex())
        print(conv)
        print(bin(int(conv, 16)))
        return packet






if __name__ == "__main__":
    r = udpScraper(None)
    print(r.getConnectRequestPacket())
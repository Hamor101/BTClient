import random
import struct
from numpy import uint64, uint32, iinfo


class UDPRequester:
    def __init__(self):
        try:
            self.protocolID = uint64(0x41727101980)
            self.action = uint32(iinfo(uint32).max - 1)
            self.transactionID = uint32(iinfo(uint32).max - 1)#self.getRandom32()
            self.connnectionID = uint32()
        except OverflowError:
            print("[UDPRequester __init__]: \033[41mError:\033[0m Packet variable out of bounds")
            return


    def getRandom32(self):
        return uint32(random.randint(1, iinfo(uint32).max))

    def getConnectRequestPacket(self):

        #Combine action (uint32) and transaction ID (uint32) into a uint64
        combined = uint64(self.action)
        combined = combined << 32
        combined = combined | self.transactionID


        packet = struct.pack(">QQ", self.protocolID, combined)
        conv = "0x" + str(packet.hex())
        print(bin(int(conv, 16)))
        return packet



if __name__ == "__main__":
    r = UDPRequester()
    print(type(r.getConnectRequestPacket()))

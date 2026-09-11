import random
import struct
import socket
from numpy import uint64, uint32, iinfo
# Conversion constant from bytes to bits
BYTES = 8


class udpScraper:

    dataSizes = {"action":32,
                 "transaction_id":32,
                 "connection_id":64}

    def __init__(self, trackerAddress:tuple, info:bytes):

        self.iHash = info
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.trackerAddress = trackerAddress

        self.protocolID     = uint64(0x41727101980)
        self.action         = uint32(0)                     #uint32(iinfo(uint32).max - 1)
        self.transactionID  = self.getRandom32()     #uint32(iinfo(uint32).max)
        self.connnectionID  = uint32(0)              #uint32(iinfo(uint32).max)


    def getRandom32(self):
        return uint32(random.randint(1, iinfo(uint32).max))

    def getConnectRequestPacket(self):
        self.action = uint32(0)
        combined = uint64(self.action)
        combined = combined << 32
        combined = combined | self.transactionID

        packet = struct.pack(">QQ", self.protocolID, combined)
        return packet

    def getScrapeRequestPacket(self):
        self.action = 2

        combined = uint64(self.action)
        combined = combined << 32
        combined = combined | self.transactionID

        packet = struct.pack(">QQ20s", self.connnectionID, combined, self.iHash)
        return packet

    def decodeConnectResponsePacket(self, responsePacket):
        packetStructure = [self.dataSizes["transaction_id"], self.dataSizes["connection_id"]]

        packetData = []
        buffer = ""

        for i in packetStructure:
            buffer = responsePacket[:i:]
            responsePacket = responsePacket[i::]
            packetData.append(buffer)
        return packetData

    def decodeErrorPacket(self, packet):
        packetStructure = []
        packetData = [packet[:self.dataSizes["transaction_id"]:], packet[self.dataSizes["transaction_id"]::]]
        return packetData

    def decodePacket(self, packet):
        packet = self.hexToBinaryLossless(packet)
        # action_id : (decoderFunctionName, packetExpectedSize)
        actions = {0:(self.decodeConnectResponsePacket, 16*BYTES), 1:None, 2:None, 3:(self.decodeErrorPacket, 8*BYTES)}
        # Find the function from the actions dictionary corresponding to the action field of the response packet
        action_field = int(packet[:self.dataSizes["action"]:],2)
        action_tuple = actions[action_field]
        if len(packet) < action_tuple[1]:
            print("[*] Size of response packet is not correct for this response type. Exiting...")
            exit(1)

        # strip the packet of the action field, call the function, and provide it as an argument
        return (action_tuple[0](packet[self.dataSizes["action"]::]), action_field)

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
    connPack = r.getConnectRequestPacket()
    r.sendRequest(connPack)
    resp = r.listen()

    tId = 0
    # with open("connect_response.bin", "rb") as f:
    #     resp = f.read()
    # with open("transactionIdTemp.txt", "r") as f:
    #     tId = f.read()
    hb = r.hexToBinaryLossless(resp)
    print(len(hb))
    print(hb)
    print(r.decodePacket(resp))
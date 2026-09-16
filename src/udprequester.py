import random
import struct
import socket
from numpy import uint64, uint32, iinfo
# Conversion constant from bytes to bits
BYTES = 8


class udpScraper:

    dataSizes = {"action":32,
                 "transaction_id":32,
                 "connection_id":64,
                 "seeders":32,
                 "completed":32,
                 "leechers":32,
                 "interval":32,
                 "ip address":32,
                 "port":16}

    actions = {"connect":uint32(0),
               "announce":uint32(1),
               "scrape":uint32(2),
               "error":uint32(3)}

    def __init__(self, trackerAddress:tuple, info:bytes):

        self.iHash = info
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.trackerAddress = trackerAddress

        # self.action         = uint32(0)                   #uint32(iinfo(uint32).max - 1)
        # self.transactionID  = self.getRandom32()          #uint32(iinfo(uint32).max)
        self.protocolID     = uint64(0x41727101980)
        self.connnectionID  = uint64(0)                     #uint32(iinfo(uint32).max)

    def getFieldSizes(self, fields:list):
        return [self.dataSizes[i] for i in fields]

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

    def getRandom32(self):
        return uint32(random.randint(1, iinfo(uint32).max))

    def getConnectRequestPacket(self):
        action = self.actions["connect"]
        transaction_id = self.getRandom32()

        combined = uint64(action)
        combined = combined << 32
        combined = combined | transaction_id

        packet = struct.pack(">QQ", self.protocolID, combined)
        return packet

    def getScrapeRequestPacket(self, iHashes:list = None):
        action = self.actions["scrape"]
        transaction_id = self.getRandom32()

        combined = uint64(action)
        combined = combined << 32
        combined = combined | transaction_id
        if iHashes == None:
            packet = struct.pack(">QQ20s", self.connnectionID, combined, self.iHash)
        else:
            packet = struct.pack((">QQ" + "20s"*len(iHashes)), self.connnectionID, combined, *iHashes)
        return packet

    def decodeConnectPacket(self, packet):
        fields = [self.dataSizes["transaction_id"], self.dataSizes["connection_id"]]
        packetData = []

        for i in fields:
            packetData.append(packet[:i:])
            packet = packet[i::]
        return packetData

    def decodeErrorPacket(self, packet):
        packetData = [packet[:self.dataSizes["transaction_id"]:], packet[self.dataSizes["transaction_id"]::]]
        return packetData

    def decodeScrapePacket(self, packet, n_scrapes = 1):
        fields = [self.dataSizes["seeders"], self.dataSizes["completed"], self.dataSizes["leechers"]]
        packetData = []

        packetData.append(packet[:self.dataSizes["transaction_id"]:])
        packet = packet[self.dataSizes["transaction_id"]::]
        for _ in range(n_scrapes):
            for j in fields:
                packetData.append(packet[:j:])
                packet = packet[j::]
        return packetData

    def decodeAnnouncePacket(self, packet):
        fields = ["transaction_id", "interval", "leechers", "seeders"]
        extraFields = ["ip address", "port"]
        extraFields = self.getFieldSizes(extraFields)
        fields = self.getFieldSizes(fields)
        packetData = [packet[fields[i]+ (i-1)*32:fields[i]+ i*32:] for i in range(len(fields))]
        seeders = int(packetData[3],2)
        packet = packet[sum(fields)::]

        for _ in range(seeders):
            for j in extraFields:
                packetData.append(packet[:j:])
                packet = packet[j::]

        return packetData
        
    def decodePacket(self, packet:bytes):
        packet = self.hexToBinaryLossless(packet)
        # action_id : (decoderFunctionName, packetExpectedSize)
        actions = {0:(self.decodeConnectPacket, 16*BYTES), 1:(self.decodeAnnouncePacket, 20*BYTES), 2:(self.decodeScrapePacket, 8*BYTES), 3:(self.decodeErrorPacket, 8*BYTES)}
        # Find the function from the actions dictionary corresponding to the action field of the response packet
        action_field = int(packet[:self.dataSizes["action"]:],2)
        action_tuple = actions[action_field]
        if len(packet) < action_tuple[1]:
            print("[*] Size of response packet is not correct for this response type. Exiting...")
            exit(1)
        if action_field == 3:
            print(f"\033[41m[*]\033[0m UDP Tracker Error. Message:{packet[self.dataSizes["action"]::]}")

        # strip the packet of the action field, call the function, and provide it as an argument
        return action_tuple[0](packet[self.dataSizes["action"]::])

    def sendPacket(self, request:bytes):
        self.socket.sendto(request, self.trackerAddress)

    def connect(self):
        packet = self.getConnectRequestPacket()
        self.sendRequest(packet)
        resp = self.listen()
        resp = self.decodePacket(resp)
        self.connnectionID = uint64(int(resp[1], 2))
        print(f"\033[44m[*]\033[0m New connection ID: {str(bin(self.connnectionID))[2::]}" )
        return resp

    def listen(self):
        resp, addr = self.socket.recvfrom(4096)
        # print(resp)
        return resp

    def request(self, requestType:str):
        ...
    


if __name__ == "__main__":
    r = udpScraper((socket.gethostbyname("tracker.opentrackr.org"), 1337), None)
    # r.connect()
    
    with open("announce_response.bin", "rb") as f:
        resp = f.read()
    # resp = r.hexToBinaryLossless(resp)
    print(resp.hex())
    # r.decodeAnnouncePacket(resp)
    print(r.decodePacket(resp))

    # packet = r.getConnectRequestPacket()
    # r.sendRequest(packet)
    # resp = r.listen()

    # tId = 0
    # with open("transactionIdTemp.txt", "r") as f:
    #     tId = f.read()
    # hb = r.hexToBinaryLossless(resp)
    # print(len(hb))
    # print(hb)
    # dec = r.decodeConnectResponsePacket(resp)
    # print(dec)
    # print(r.hexToBinaryLossless())
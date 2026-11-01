# Implement class for creating, sending, receiving, decoding packets for use with bittorrent UDP trackers.

import random
import struct
import socket
import os
import hashlib
from numpy import uint64, uint32, uint16, int32, iinfo

# Conversion constant from bytes to bits
BYTES = 8


class udpScraper:

    dataSizes = {"connection_id"    :64,
                 "action"           :32,
                 "err_msg"          :32,
                 "transaction_id"   :32,
                 "seeders"          :32,
                 "completed"        :32,
                 "leechers"         :32,
                 "interval"         :32,
                 "ip_address"       :32,
                 "port"             :16}

    actions = {"connect"    :uint32(0),
               "announce"   :uint32(1),
               "scrape"     :uint32(2),
               "error"      :uint32(3)}

    def __init__(self, trackerAddress:tuple, info:bytes, programState:dict, starttime:int):

        self.iHash          = info
        self.socket         = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.trackerAddress = trackerAddress

        self.transactionID  = self.getRandom32()          #uint32(iinfo(uint32).max)
        self.protocolID     = uint64(0x41727101980)
        self.connectionID   = uint64(0)                   #uint64(iinfo(uint64).max)
        self.peerID         = self.generatePeerId(starttime)
        self.state          = programState
        self.key            = 0

    def binaryToIpConverter(self, ip:str):
        octets = [str(int(ip[(i-1)*8:i*8],2)) for i in range(1,5)]
        ip = ".".join(octets)
        return ip

    def generatePeerId(self, startuptime):
        peerId = b""
        startuptime = int(startuptime)
        process_id = os.getpid()
        peerId = hashlib.sha1((str(process_id) + str(startuptime)).encode()).digest()
        return peerId

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
        self.transactionID = self.getRandom32()

        packet = struct.pack(">QLL", self.protocolID, action, self.transactionID)
        return packet

    def getScrapeRequestPacket(self, iHashes:list = None):
        action = self.actions["scrape"]
        self.transactionID = self.getRandom32()

        if iHashes == None:
            packet = struct.pack(">QLL20s", self.connectionID, action, self.transactionID,  self.iHash)
        else:
            packet = struct.pack((">QLL" + "20s"*len(iHashes)), self.connectionID, action, self.transactionID, *iHashes)
        return packet

    def getAnnounceRequestPacket(self, event, ip=uint32(0), port=uint16(0), key=uint32(0), num_want=int32(0)):
        event = uint32(event)
        num_want = int32(num_want)
        action = self.actions["announce"]
        self.transactionID = self.getRandom32()
        packet = struct.pack(">QLL20s20sQQQLLLlH",
                            self.connectionID,
                            action, 
                            self.transactionID,
                            self.iHash,
                            self.peerID,
                            self.state["downloaded"],
                            self.state["left"],
                            self.state["uploaded"],
                            event,
                            ip,
                            key,
                            num_want,
                            port
                            )
        return packet

    def decodeConnectPacket(self, packet):
        fields = [self.dataSizes["transaction_id"], self.dataSizes["connection_id"]]
        packetData = []

        for i in fields:
            packetData.append(packet[:i:])
            packet = packet[i::]
        return [int(i, 2) for i in packetData]

    def decodeErrorPacket(self, packet):
        packetData = [packet[:self.dataSizes["transaction_id"]:], packet[self.dataSizes["err_msg"]::]]
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
        output = {"transaction_id":0, "interval":1, "leechers":2, "seeders":3, "peers":4}
        fields = self.getFieldSizes(fields)
        variableFields = ["ip_address", "port"]
        variableFields = self.getFieldSizes(variableFields)
        packetData = []
        peers = []

        for i in fields:
            packetData.append(packet[:i:])
            packet = packet[i::]

        while packet:
            for i in variableFields:
                packetData.append(packet[:i:])
                packet = packet[i::]

        packetData[:4] = [int(i,2) for i in packetData[:4]]
        packetData[4::2] = [self.binaryToIpConverter(i) for i in packetData[4::2]]
        packetData[5::2] = [int(i,2) for i in packetData[5::2]]


        try:
            for k,v in output.items():
                output[k] = packetData[v]

            for i in range(4, len(packetData), 2):
                peers.append([packetData[i], packetData[i+1]])
            
            packetData = packetData[:4:]
            packetData.append(peers)
        except IndexError:
            print("\033[43m[*]\033[0m Tracker returned no peers. (num_want=0)")

        return packetData

    def decodePacket(self, packet:bytes):
        errBackup = packet
        packet = self.hexToBinaryLossless(packet)
        actions = {0:(self.decodeConnectPacket, 16*BYTES), 1:(self.decodeAnnouncePacket, 20*BYTES), 2:(self.decodeScrapePacket, 8*BYTES), 3:(self.decodeErrorPacket, 8*BYTES)}
        action_field = int(packet[:self.dataSizes["action"]:],2)
        action_tuple = actions[action_field]
        if len(packet) < action_tuple[1]:
            print("[*] Size of response packet is not correct for this response type. Exiting...")
            exit(1)
        if action_field == 3:
            print(f"\033[41m[*]\033[0m UDP Tracker Error. Message: \033[41m[{errBackup[self.dataSizes["action"]//4::].decode()}]\033[0m")

        # Decoder function receives packet WITHOUT the [action] field
        return action_tuple[0](packet[self.dataSizes["action"]::])

    def sendPacket(self, request:bytes):
        self.socket.sendto(request, self.trackerAddress)

    def connect(self):
        packet = self.getConnectRequestPacket()
        self.sendPacket(packet)
        resp = self.listen()
        resp = self.decodePacket(resp)
        self.connectionID = uint64(resp[1])
        print(f"\033[44m[*]\033[0m New connection ID: {str(bin(self.connectionID))[2::]}" )
        return resp

    def scrape(self, info_hashes:list = None):
        if not self.connectionID:
            self.connect()
        request = self.getScrapeRequestPacket(info_hashes)
        self.sendPacket(request)
        response = self.listen()
        return self.decodePacket(response)

    def announce(self, event="None", num_want=-1, ret_ip=0, ret_port=0):
        eventsMap = {"None":0, "Completed":1, "Started":2, "Stopped":3}
        event = eventsMap[event]
        if not ret_port:
            ret_port = self.state["port"]
        if not self.connectionID:
            self.connect()
        request = self.getAnnounceRequestPacket(event, ret_ip, ret_port, self.key, num_want)
        self.sendPacket(request)
        response = self.listen()
        return self.decodePacket(response)
    
    def listen(self):
        resp, addr = self.socket.recvfrom(4096)
        return resp
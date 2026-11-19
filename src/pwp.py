# Implement bittorrent peer wire protocol
import struct
import random

import udp_tracker  # remove later


class Peer():
    def __init__(self, ip, port, pid):
        self.ip = ip
        self.port = port
        self.peer_id = pid
        self.am_choking = True
        self.am_interested = False
        self.is_choking = True
        self.is_interested = False

        
class PeerMessage():
    msgs = [("keep-alive"), ("choke"), ("unchoke"), ("interested"), ("not-interested"), ("have", 15), ("bitfield", b"123432"), ("request", 1,2,3), ("piece", 4,5,b"ababdhasbdsb"), ("cancel", 1,2,3), ("port", 1337)]
    msgNamemsgIdMap = {"keep-alive"     :-1,
                       "choke"          :0,
                       "unchoke"        :1,
                       "interested"     :2,
                       "not-interested" :3,
                       "have"           :4,
                       "bitfield"       :5,
                       "request"        :6,
                       "piece"          :7,
                       "cancel"         :8,
                       "port"           :9}

    msgIdFormatStrMap = {-1     :("I",0),
                         0      :("IB",1),
                         1      :("IB",1),
                         2      :("IB",1),
                         3      :("IB",1),
                         4      :("IBI",5),
                         6      :("IBIII",13),
                         8      :("IBIII",13),
                         9      :("IBH",3)}

    variableLenPayloadMap = {5:("IB", 1),
                             7:("IBHH", 9)}

    def __init__(self, msgName, *payload):
        try:
            if self.msgNamemsgIdMap[msgName] in [5, 7]:
                self.varLenMessage(msgName, *payload)
            else:
                self.fixedLenMessage(msgName, *payload)
        except KeyError:
            print(f"\033[41m[*]\033[0mUnknown message type: {msgName}")


    def fixedLenMessage(self, messageName, *payload):
        messageId = self.msgNamemsgIdMap[messageName]
        formatStr = self.msgIdFormatStrMap[messageId][0]
        length    = self.msgIdFormatStrMap[messageId][1]
        try:
            if messageId >= 0:
                self.packet = struct.pack(">" + formatStr, length, messageId, *payload)
            else:
                self.packet = struct.pack(">" + self.msgIdFormatStrMap[-1][0], 1)
        except struct.error as e:
            print(f"\033[41m[*]\033[0m] Error: Could not pack message with fixed-length ({messageName})")
            print(f"\033[41m[*]\033[0m:::: {e}")

    def varLenMessage(self, messageName, *payload):
        {"bitfield":self.bitfield, "piece":self.piece}[messageName](*payload)


    def bitfield(self, bitfield):
        messageId = self.msgNamemsgIdMap["bitfield"]
        payloadLenTuple = self.variableLenPayloadMap[messageId]
        formatStr = ">" + payloadLenTuple[0] + str(len(bitfield)) + "s"
        try:
            self.packet = struct.pack(formatStr, payloadLenTuple[1] + len(bitfield), messageId, bitfield)
        except struct.error as e:
            print("\033[41m[*]\033[0m Error: Could not pack \'bitfield\' message.")
            print(f"\033[41m[*]\033[0m:::: {e}")
        

    def piece(self, index, begin, block):
        messageId = self.msgNamemsgIdMap["piece"]
        payloadLenTuple = self.variableLenPayloadMap[messageId]
        formatStr = ">" + payloadLenTuple[0] + str(len(block))+"s"
        try:
            self.packet = struct.pack(formatStr, payloadLenTuple[1] + len(block), messageId, index, begin, block)
        except struct.error as e:
            print("\033[41m[*]\033[0m Error: Could not pack \'piece\' message.")
            print(f"\033[41m[*]\033[0m:::: {e}")
        
class PeerManager():
    def __init__(self, own_id):
        self.peers = []
        self.myID = own_id

    def addPeer(self, ip, port, pid):
        self.peers.append(Peer(ip,port,pid))

    def findPeer(self, pid):
        for i in range(len(self.peers)):
            if self.peers[i].peer_id == pid:
                break
        return i

    def handshake(self, iHash):
        PSTR = b"BitTorrent Protocol"
        PSTRLEN = 19
        p1 = struct.pack(">b19s" + 8*"x" + "20s20s", PSTRLEN, PSTR, iHash, self.myID)
        print(p1)



if __name__ == "__main__":
    # with open("info_hash.bin", "rb") as f:
    #     ih = f.read()
    # pm =  PeerManager(b"111")
    # pm.handshake(ih)
    ut = udp_tracker.udpScraper((), b"", {}, 0)
    args = [["keep-alive"], ["choke"], ["unchoke"], ["interested"], ["not-interested"], ["have", 15], ["bitfield", b"123432"], ["request", 1,2,3], ["piece", 4,5,b"ababdhasbdsb"], ["cancel", 1,2,3], ["port", 1337]]
    for i in args:
        pm = PeerMessage(*i)
        print(f"\033[44m{i[0]}\033[0m:")
        print(ut.hexToBinaryLossless(pm.packet))
        
    # pm.payloadMsg("request", 1, 320)
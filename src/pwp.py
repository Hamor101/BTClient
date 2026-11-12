# Implement bittorrent peer wire protocol
import struct
import random

class Peer():
    def __init__(self, ip, port, pid):
        self.ip = ip
        self.port = port
        self.peer_id = pid
        self.am_choking = True
        self.am_interested = False
        self.is_choking = True
        self.is_interested = False


class peerMessage():

    msgNamemsgIdMap = {"choke"          :0,
                       "unchoke"        :1,
                       "interested"     :2,
                       "not interested" :3,
                       "have"           :4,
                       "bitfield"       :5,
                       "request"        :6,
                       "piece"          :7,
                       "cancel"         :8,
                       "port"           :9
                       }

    msgIdFormatStrMap = {0: "Ic",
                         1:"Ic",
                         2:"Ic",
                         3:"Ic",
                         4:"IcI",
                         6:"IcIII",
                         8:"IcIII",
                         9:"IcH"}

    def __init__(self, len_prefix, message_id, payload):
        try:
            if len_prefix == 0:                             # Keep-alive message
                self.packet = struct.pack(4*"x")
            elif message_id >= 0 and message_id <= 3:       # Messages with no payload
                self.packet = struct.pack(self.msgIdFormatStrMap[message_id], len_prefix, message_id)
            elif message_id in self.msgIdFormatStrMap:
                self.packet = struct.pack(self.msgIdFormatStrMap[message_id], len_prefix, message_id, payload)
            elif message_id not in self.msgIdFormatStrMap:
                self.variableLenMessage(message_id, payload)
        except struct.error:
            print(f"\033[41m[*]\033[0m {__class__} Error: Cannot construct peer message: Incorrect format given to struct.pack()")


    def variableLenMessage(self, message_id, payload):
        length = len(payload)
        formatStrMap = {5:"Ic" + str(length) + "s",
                        7:"IcII" + str(length) +"s"}
        self.packet = struct.pack(formatStrMap[message_id], length, message_id, payload)
        

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
    mymsg = peerMessage()
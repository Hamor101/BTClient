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
    with open("info_hash.bin", "rb") as f:
        ih = f.read()
    pm =  PeerManager()
    pm.handshake(ih)
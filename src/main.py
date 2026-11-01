import time
import random
import os

import bencoding
import http_tracker
import printer
import udp_tracker

startuptime = time.time()

def getPeerID():
    stime = str(startuptime)
    process_id = str(os.getpid())
    ID = "".join(["".join([str(random.randint(0,9)) for _ in range(20 - (len(process_id) + len(stime)))]), stime, process_id])
    return ID.encode()

peerID = getPeerID()


#TODO: Remove later, make it use argparse for path
PATH = "../testfiles/"
file_path = PATH + "/" + "test_torrent.torrent"
#########################################################

fileParser = bencoding.Decoder(file_path, True)
metainfo = fileParser.decodeFile()
info_hash = fileParser.getInfoHash()

printer.printDict(metainfo)

program_state = {"port":0, "uploaded":0, "downloaded":0, "left": fileParser.getLenBytes(), "peer_id": peerID}
program_state["port"] = random.randint(6881, 6889)

time_taken = time.time() - startuptime
print(f"TIME TAKEN:{time_taken*1000} ms")

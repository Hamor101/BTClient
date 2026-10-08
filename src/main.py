import time
import random

import bencoding
import http_tracker
import printer
import udp_tracker

startuptime = time.time()

#TODO: Remove later, make it use argparse for path
PATH = "C:/Users/Hamor_odz16ig/documents/code projects/python/bittorrent/testfiles"
file_path = PATH + "/" + "test_torrent.torrent"

# metainfo.metaInfo(file_path)

fileParser = bencoding.Decoder(file_path, True)
metainfo = fileParser.decodeFile()
info_hash = fileParser.getInfoHash()



program_state = {"port":0, "uploaded":0, "downloaded":0, "left": fileParser.getLenBytes()}
program_state["port"] = random.randint(6881, 6889)

# resp = http_tracker.HTTP_announce(metainfo, info_hash, startuptime, program_state, "None")
with open("http_tracker_response.bin", "rb") as f:
   resp = f.read()

# printer.printDict(bencoding.Decoder("http_tracker_response.bin", True).decodeFile())


# printer.printDict()
# printer.printDict(metainfo)



time_taken = time.time() - startuptime
print(f"TIME TAKEN:{time_taken*1000} ms")

import time
import random

import bencoding
import trackerget
import printer
import udprequester
import hashlib

startuptime = time.time()

#TODO: Remove later, make it use argparse for path
PATH = "C:/Users/Hamor_odz16ig/documents/code projects/python/bittorrent/testfiles"
file_path = PATH + "/" + "test_torrent.torrent"


decoderObject = bencoding.Decoder(file_path, True)
metainfo = decoderObject.decodeFile()
info_hash = decoderObject.getInfoHash()
piece_len = metainfo[b'info'][b'piece length']
num_pieces = len(metainfo[b'info'][b'pieces']) / 20
program_state = {"port":0, "uploaded":0, "downloaded":0, "left": decoderObject.getLenBytes()}
program_state["port"] = random.randint(6881, 6889)
program_state["left"] = decoderObject.getLenBytes()
# printer.printDict(metainfo)
# print(metainfo)

r = udprequester.udpScraper(('tracker.opentrackr.org', 1337),info_hash, program_state, startuptime)
print(r.announce(1, -1))
# r.connect()
# pack = r.getAnnounceRequestPacket(0, num_want=10)
# r.sendPacket(pack)
# resp = r.listen()



time_taken = time.time() - startuptime
print(f"TIME TAKEN:{time_taken*1000} ms")

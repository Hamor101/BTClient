import time
import random

import bencoding
import trackerget
import printer

startuptime = time.time()

#TODO: Remove later, make it use argparse for path
PATH = "C:/Users/Hamor_odz16ig/documents/code projects/python/bittorrent/testfiles"
file_path = PATH + "/" + "[nCore][ebook]Chugong_-_Solo_Leveling_Vol._1.torrent"


decoderObject = bencoding.Decoder(file_path)
metainfo = decoderObject.decodeFile()
info_hash = decoderObject.getInfoHash()
piece_len = metainfo[b'info'][b'piece length']
num_pieces = len(metainfo[b'info'][b'pieces']) / 20
printer.printDict(metainfo)


program_state = {"port":0, "uploaded":0, "downloaded":0, "left":0}
program_state["port"] = random.randint(6881, 6889)
program_state["left"] = decoderObject.getLenBytes()

trackerRespData = trackerget.scrapeHTTPTracker(metainfo, info_hash, startuptime, program_state, "stopped")
decoderObject = bencoding.Decoder(data=trackerRespData, file=False)

tracker_response = decoderObject.decodeDict()
printer.printDict(tracker_response)
# print(tracker_response["interval"])


time_taken = time.time() - startuptime
print(f"TIME TAKEN:{time_taken*1000} ms")

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
program_state = {"port":0, "uploaded":0, "downloaded":0, "left":0}
program_state["port"] = random.randint(6881, 6889)
program_state["left"] = decoderObject.getLenBytes()
# printer.printDict(metainfo)
# print(metainfo)

r = udprequester.udpScraper(('tracker.opentrackr.org', 1337),info_hash)
hashes = [b"hello", b"how r u", b"hi", b"greetings!"]
hashes = [hashlib.sha1(i).digest() for i in hashes]
out = r.hexToBinaryLossless(r.getScrapeRequestPacket(hashes))
out = out[128::]


# Everything below this is only for testing
out = [out[i-160:i:] for i in range(160, len(out), 160)]
# out2 = [out2[i-1:i:] for i in range(1, len(out2)-1, 80)]
hashes = [r.hexToBinaryLossless(i) for i in hashes]
for hsh in range(len(out)):
    print(f"{out[hsh]}:\n{hashes[hsh]}", end="\n\n")
# print("\n\n\n")
# for hsh in hashes:
#     print(hsh, end="\n\n")
# print(hashes, sep="\n")
# r.connect()
# requestPacket = r.getScrapeRequestPacket()
# r.sendPacket(requestPacket)
# resp = r.listen()
# with open("scrapeResponse.bin", "rb") as f:
#     resp = f.read()
# print(r.hexToBinaryLossless(resp))
# decodedData = r.decodePacket(resp)
# print(f"Transaction_ID: {decodedData[0]}\nSeeders: {int(decodedData[1],2)}\nCompleted:{int(decodedData[2], 2)}\nLeechers:{int(decodedData[3], 2)}")


# with open("scrapeResponse.bin", "wb") as f:
#     f.write(resp)
# trackerRespData = trackerget.scrapeHTTPTracker(metainfo, info_hash, startuptime, program_state, "stopped")
# decoderObject = bencoding.Decoder(data=trackerRespData, file=False)
# tracker_response = decoderObject.decodeDict()
# printer.printDict(tracker_response)


time_taken = time.time() - startuptime
print(f"TIME TAKEN:{time_taken*1000} ms")

import os
import requests
import hashlib


def generatePeerId(startuptime):
    peerId = b""
    startuptime = int(startuptime)
    process_id = os.getpid()
    peerId = (str(process_id) + str(startuptime)).encode()
    return peerId

def HTTP_announce(metainfo, info_hash, startuptime, programState, event):
    startuptime = int(startuptime)
    uribase = metainfo[b'announce'].decode()
    info_hash = info_hash
    pid = hashlib.sha1(generatePeerId(startuptime)).digest()

    for k in programState:
        programState[k] = str(programState[k])

    buf = []
    for i in range(len(uribase)):
        if uribase[i] == ":":
            buf = []
        if uribase[i] == "/":
            buf = []
            break
        buf.append(uribase[i])

    
    resp = requests.get(uribase, params={
        "info_hash" : info_hash, 
        "peer_id" : pid, 
        "port" : programState["port"], 
        "uploaded" : programState["uploaded"], 
        "downloaded" : programState["downloaded"], 
        "left" : programState["left"],
        "compact" : 1,
        "no_peer_id" : 0,
        "event" : event
        })
    return resp.content
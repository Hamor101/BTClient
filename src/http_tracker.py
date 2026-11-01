# Send and decode HTTP announce requests to bittorrent trackers.

import requests
import hashlib
import bencoding

class HTTPScraper:
    def __init__(self, metainfo, info_hash, startuptime, programState):
        self.metainfo = metainfo
        self.info_hash = info_hash
        self.starttime = startuptime
        self.programState = programState

    def HTTP_announce(self, event:str):
        events = {"none": 0, "completed":1, "started":2, "stopped":3}
        event = events[event.lower()]
        uribase = self.metainfo[b'announce'].decode()
        info_hash = info_hash
        pid = hashlib.sha1(self.programState["peer_id"]).digest()

        for k in self.programState:
            self.programState[k] = str(self.programState[k])

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
            "port" : self.programState["port"], 
            "uploaded" : self.programState["uploaded"], 
            "downloaded" : self.programState["downloaded"], 
            "left" : self.programState["left"],
            "compact" : 1,
            "no_peer_id" : 0,
            "event" : event
            })
        return bencoding.Decoder(resp.content, False).decodeDict()
import string
import hashlib


class Decoder:
    def __init__(self, data, file = True):
        self.data = data   # Stores raw data of the object to be decoded
        self.index = 0
        self.charMap = {'i' : 105, 'd' : 100, 'l' : 108, 'e' : 101, ':' : 58}
        self.functionMap = {105:self.decodeInt, 100:self.decodeDict, 108:self.decodeList}
        self.infoLoc = 0    # Stores info dict start
        self.infoEnd = 0    # Stores info dict end
        self.decoded = 0       # Stores decoded value of metainfo file
        if file:
            with open(data, "rb") as f:
                self.data = f.read()
        for i in range(len(self.data) -3):
            if self.data[i:i+4] == b'info':
                # print(self.data[i:i+4])
                self.infoLoc = i+4
                break

    def getInfoHash(self):
        print(hashlib.sha1(self.data[self.infoLoc:self.infoEnd]).digest())
        return hashlib.sha1(self.data[self.infoLoc:self.infoEnd]).digest()
    
    def getLenBytes(self):
        try:
            return self.decoded[b'info'][b'length']
        except KeyError:
            length = 0
            for i in self.decoded[b'info'][b'files']:
                length += i[b'length']
            return length

    def decodeFile(self):
        self.decoded = self.functionMap[self.data[self.index]]()
        return self.decoded

    def decodeInt(self) -> int:
        initial = self.index
        while self.data[self.index] != self.charMap['e']:
            self.index += 1
        return int(self.data[initial+1:self.index])
    
    def decodeStr(self) -> str:
        initial = self.index
        while self.data[self.index] != b':'[0]:
            self.index += 1
        length = int(self.data[initial:self.index])
        self.index += 1
        return_value = self.data[self.index:self.index + length]
        self.index += length -1
        return return_value
    
    def decodeList(self) -> list:
        l = []
        self.index += 1
        while self.data[self.index] != self.charMap['e']:
            if self.data[self.index] in self.functionMap:
                l.append(self.functionMap[self.data[self.index]]())
            elif self.data[self.index] in string.digits.encode():
                l.append(self.decodeStr())
            self.index += 1
        return l

    def decodeDict(self) -> dict:
        d = {}
        self.index += 1
        isKey = True
        keyBuffer = b""
        while self.data[self.index] != self.charMap['e']:
            if isKey:
                keyBuffer = self.decodeStr()
                isKey = False
            elif self.data[self.index] in self.functionMap:
                d[keyBuffer] = self.functionMap[self.data[self.index]]()
                isKey = True
            elif self.data[self.index] in string.digits.encode():
                d[keyBuffer] = self.decodeStr()
                isKey = True
            self.index += 1
            self.infoEnd = (self.index if keyBuffer == b'info' else self.infoEnd) 
        return d
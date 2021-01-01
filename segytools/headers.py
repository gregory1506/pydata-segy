import json
from struct import unpack

class BinaryHeader:
    def __init__(self, buffer, binhdrdef):
        if len(buffer) != 400:
            print("Binary header should be 400 bytes long")
        else:
            with open(binhdrdef) as json_file:
                data = json.load(json_file)
            for key in data:
                name, endianness, typ, start, end = data[key]
                setattr(self, name, unpack(endianness+typ, buffer[start:end])[0])

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

class TraceHeader:
    def __init__(self, buffer, trchdrdef):
        if len(buffer) != 240:
            print("Trace header should be 240 bytes long")
        else:
            with open(trchdrdef) as json_file:
                data = json.load(json_file)
            for key in data:
                name, endianness, typ, start, end = data[key]
                setattr(self, name, unpack(endianness+typ, buffer[start:end])[0])

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]
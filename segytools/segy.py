import os
from .headers import BinaryHeader, TraceHeader
from numba import vectorize
import numpy as np
import pandas as pd

@vectorize(['float32(uint32)'])
def ibm32toieee32(data):
    if data == 0:
        return 0.0
    sign = data >> 31 & 0x01
    exponent = data >> 24 & 0x7f
    mantissa = (data & 0x00ffffff) / float(pow(2, 24))
    return (1 - 2 * sign) * mantissa * pow(16.0, exponent - 64)

class segy(object):

    def __init__(self, filepath=None, binhdrdef=None, trchdrdef=None):
        ''' instantiate segy object. 
        filepath (str) is absolute path to segy file
        binhdrdef (str) is absolute path to json file that describes binary header
        trchdrdef (str) is absolute path to json file that describes trace header
        '''
        if filepath is None:
            raise ValueError("must provide valid filepath")
        else:
            self.number_of_bytes = os.path.getsize(filepath) #raises OSError if inaccesible or does not exist
            f = open(filepath,"rb")
            self.ebcdic = self.read_ebcdic(f.read(3200))
            self.bin = BinaryHeader(f.read(400), binhdrdef)
            self.hdrs, self.trcs = self.readsegy(f, trchdrdef)
            f.close()

    def read_ebcdic(self, buffer):
        try:
            tmp = buffer.decode("utf-8").strip("@")
        except:
            tmp = buffer.decode("cp037").strip("@")
        return tmp

    def readsegy(self, f, trchdrdef):
        hdrs, trcs, idx = [], [], 1
        samples_per_trace = self.bin.ns
        print("Starting loop....")
        while True:
            tmp = f.read(240)
            if not tmp:
                print("End scanning .......")
                break
            hdr = TraceHeader(tmp,trchdrdef).__dict__
            trc = f.read(samples_per_trace*4)
            arr = ibm32toieee32(np.frombuffer(trc,dtype='>u4'))
            hdrs.append(hdr)
            trcs.append(arr)
            idx+=1
            if idx % 10000 == 0:
                print(f"Reading trace {idx}")
        df = pd.DataFrame(hdrs)
        trcs = np.array(trcs)
        return (df.copy(),trcs)




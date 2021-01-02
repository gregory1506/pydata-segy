import os
from numba import vectorize
import numpy as np
import pandas as pd
from netCDF4 import Dataset 
import json
from struct import unpack

@vectorize(['float32(uint32)'])
def ibm32toieee32(data:int)->float:
    if data == 0:
        return 0.0
    sign = data >> 31 & 0x01
    exponent = data >> 24 & 0x7f
    mantissa = (data & 0x00ffffff) / float(pow(2, 24))
    return (1 - 2 * sign) * mantissa * pow(16.0, exponent - 64)

def make_bin_hdr(buffer:bytes, data:dict)->dict:
    d = {}
    if len(buffer) != 400:
        print("Trace header should be 240 bytes long")
    else:
        for key in data:
            name, endianness, typ, start, end = data[key]
            d[name] = unpack(endianness+typ, buffer[start:end])[0]
    return d

def make_trc_hdr(buffer:bytes, data:dict)->dict:
    d = {}
    if len(buffer) != 240:
        print("Trace header should be 240 bytes long")
    else:
        for key in data:
            name, endianness, typ, start, end = data[key]
            d[name] = unpack(endianness+typ, buffer[start:end])[0]
    return d

def read_ebcdic(buffer:bytes)->str:
    try:
        tmp = buffer.decode("utf-8").strip("@")
    except:
        tmp = buffer.decode("cp037").strip("@")
    return tmp

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
            with open(binhdrdef,"rb") as f:
                self.binary_hdr_mapping = json.load(f)
            with open(trchdrdef,"rb") as f:
                self.trace_hdr_mapping = json.load(f)
            with open(filepath,"r+b") as f:
                self.ebcdic = read_ebcdic(f.read(3200))
                self.bin = make_bin_hdr(f.read(400), self.binary_hdr_mapping)
            self.headers, self.traces = self.readsegy(filepath)

    def readsegy(self, filepath):
        hdrs, trcs, idx = [], [], 1
        samples_per_trace = self.bin['ns']
        print("Starting loop....")
        with open(filepath,"r+b") as f:
            f.read(3600)
            while True:
                tmp = f.read(240)
                if not tmp:
                    print("End scanning .......")
                    break
                hdr = make_trc_hdr(tmp,self.trace_hdr_mapping)
                trc = f.read(samples_per_trace*4)
                arr = ibm32toieee32(np.frombuffer(trc,dtype='>u4'))
                hdrs.append(hdr)
                trcs.append(arr)
                idx+=1
                if idx % 10000 == 0:
                    print(f"Reading trace {idx}")
        df = pd.DataFrame(hdrs)
        trcs = np.array(trcs)
        return (df,trcs)

    def to_netcdf4(self, dataname=None, datadef=None):
        cols = self.headers.columns
        with open(datadef) as json_file:
            data = json.load(json_file)
        print("creating netcdf file")
        ds = Dataset(dataname,"w","NETCDF4")
        for dim in data["dims"]:
            if dim in cols:
                ds.createDimension(dim,len(self.headers[dim].unique()))
            else:
                raise ValueError(f"dimension {dim} not found in headers")
        ds.createDimension('samples',self.bin['ns'])
        print("Created dimensions...")
        dims = tuple(ds.dimensions.keys())
        for var in data["variables"]:
            if var in dims and var in cols:
                ds.createVariable(var, "i4", var)
                ds[var][:] = self.headers[var].unique()
            if var not in dims and var in cols:
                ds.createVariable(var, "i4", dims[:-1])
                ds[var][:] = self.headers[var].values.reshape(ds[var].shape)
            if var == 'samples':
                ds.createVariable("samples", "i4" , "samples")
                si = self.bin["si"] // 1000
                ds["samples"][:] = np.arange(0, self.bin['ns'], dtype=np.timedelta64(si,"ms"))
            if var == 'data':
                ds.createVariable("data", "f4", dims)
                ds["data"][:] = np.array(self.traces).reshape(ds["data"].shape)
            ds[var].setncatts(data['variables'][var])
            print(f"Created variable {var}")
        ds.close()
        print("completed .... ")



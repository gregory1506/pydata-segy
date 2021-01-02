from segytools import segy
import re

segy_file_path = "./Kerry3D.segy"
binary_hdr_path = "./segytools/default_binhdr.json"
trace_hdr_path = "./segytools/deafult_trchdr.json"

if __name__ == "__main__":
    kerry = segy.segy(filepath=segy_file_path, binhdrdef=binary_hdr_path,\
                      trchdrdef=trace_hdr_path)
    # print(kerry.ebcdic)
    # print(kerry.bin.__dict__)
    # print(kerry.hdrs.head())
    # print(kerry.trcs.shape)
    kerry.to_netcdf4("./kerry.nc", datadef="./segytools/default_netcdf.json")
from segytools import segy
import re

if __name__ == "__main__":
    kerry = segy.segy("./Kerry3D.segy", \
            binhdrdef="./segytools/default_binhdr.json",\
                trchdrdef="./segytools/deafult_trchdr.json")
    # print(re.sub(r"(C\d+ )","\n\1 ", kerry.ebcdic))
    # print(kerry.ebcdic.replace(r"(C\d+ )","\n\1 "))
    # print(kerry.bin.__dict__)
    print(kerry.hdrs.head())
    print(kerry.trcs.shape)
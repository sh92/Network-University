import hashlib
import sys

class md5Check:
    def __init__(self,filePath):
        self.filePath = filePath

    def calc_md5(self, block_size=8192):
        md5 = hashlib.md5()
        try:
            f=open(self.filePath,'rb')
        except IOError as e:
            print(e)
            return
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            md5.update(buf)
        return md5.hexdigest()

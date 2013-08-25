from JumpScale import j

try:
    import hashlib
except:
    pass
try:
    import blosc
except:
    pass
try:
    import mhash
except:
    pass

class DispersedBlock:
    def __init__(self):
        self.subblocks=[]

    def create(self,s,nrblocks, extrablocks,compress=True):
        pass
        
class ByteProcessor:
    @staticmethod
    def hashMd5(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        impl = hashlib.md5(s)
        return impl.hexdigest()

    @staticmethod
    def hashTiger160(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        h=mhash.MHASH(mhash.MHASH_TIGER160,s)
        return h.hexdigest()

    @staticmethod
    def hashTiger160bin(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        h=mhash.MHASH(mhash.MHASH_TIGER160,s)
        return h.digest()

    @staticmethod
    def hashTiger192(s):
        h=mhash.MHASH(mhash.MHASH_TIGER,s)
        return h.hexdigest()

    @staticmethod
    def compress(s):
        return blosc.compress(s, typesize=8)

    @staticmethod
    def decompress(s):
        return blosc.decompress(s)

    @staticmethod
    def disperse(s,nrblocks, extrablocks,compress=True):
        """
        returns DispersedBlock object
        """
        db=DispersedBlock()
        db.create(s,nrblocks,extrablocks,compress)
        return db
        
    @staticmethod
    def getDispersedBlockObject():
        return DispersedBlock

    @staticmethod
    def undisperse(dispersedBlockObject,uncompress=True):
        dispersedBlockObject.restore



j.base.byteprocessor=ByteProcessor

from OpenWizzy import o

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
        impl = hashlib.new(s)
        return impl.hexdigest()

    def hashTiger160(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        mhash.keygen(mhash.MHASH_TIGER160,s,key_size=160)

    def hashTiger192(s):
        mhash.keygen(mhash.MHASH_TIGER192,s,key_size=192)

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

    @staticmethod
    def decompress(s):
        return blosc.decompress(s, typesize=8)

o.byteprocessor=ByteProcessor

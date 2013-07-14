from OpenWizzy import o
from LRUCache import LRUCache

class RWCache():
    def __init__(self,nrItemsReadCache,maxNrItemsWriteCache=50,maxTimeWriteCache=2000,writermethod=None):
        self.cacheR=o.db.cache.getRCache(nrItemsReadCache)
        self.cacheW=WCache(maxNrItemsWriteCache,writermethod,maxTimeWriteCache)

    def set(self,key,obj):
        self.cacheR[key]=obj
        self.cacheW[key]=obj

    def flush(self):
        from IPython import embed
        print "DEBUG NOW flush"
        embed()

#based on LRUCache but modified for different purpose (write through cache)
class WCache(LRUCache):    

    def __init__(self, size=5000,writermethod=None,maxtime=2000):
        """
        @param writermethod if given then this method will be called with max size reached or when flush called for objects older than specified maxtime
        """
        # Check arguments
        if size <= 0:
            raise ValueError, size
        elif type(size) is not type(0):
            raise TypeError, size
        object.__init__(self)
        self.__heap = []
        self.__dict = {}
        self.size = size
        self.maxtime=maxtime
        self.writermethod=writermethod
        
    def __setitem__(self, key, obj):
        if self.__dict.has_key(key):
            node = self.__dict[key]
            node.obj = obj
            node.atime = time.time()
            node.mtime = node.atime
            heapify(self.__heap)
        else:
            # size may have been reset, so we loop
            while len(self.__heap) >= self.size:
                lru = heappop(self.__heap)
                if self.writermethod<>None:
                    from IPython import embed
                    print "DEBUG NOW write through"
                    embed()
                    self.writermethod(self.__dict[lru.key])
                    del self.__dict[lru.key]
                else:
                    raise RuntimeError("write queue full")
            node = self.__Node(key, obj, time.time())
            self.__dict[key] = node
            heappush(self.__heap, node)
    
    
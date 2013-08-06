from OpenWizzy import o

class SerializersFactory():

    def __init__(self):
        self.types={}
        self._cache={}

    def get(self,serializationstr,key=""):
        """
        serializationstr FORMATS SUPPORTED FOR NOW
            m=MESSAGEPACK 
            c=COMPRESSION WITH BLOSC
            b=blowfish
            s=snappy
            j=json
            b=base64
            l=lzma
            p=pickle
            r=bin (means is not object (r=raw))
            l=log

         example serializationstr "mcb" would mean first use messagepack serialization then compress using blosc then encrypt (key will be used)

        this method returns 
        """
        k="%s_%s"%(serializationstr,key)
        if not self._cache.has_key(k):
            if len(self._cache.keys())>100:
                self._cache={}
            self._cache[k]= Serializer(serializationstr,key)
        return self._cache[k]

    def getMessagePack(self):
        return self.getSerializerType("m")

    def getBlosc(self):
        return self.getSerializerType("c")

    def getSerializerType(self,type,key=""):
        """
        serializationstr FORMATS SUPPORTED FOR NOW
            m=MESSAGEPACK 
            c=COMPRESSION WITH BLOSC
            b=blowfish
            s=snappy
            j=json
            6=base64
            l=lzma
            p=pickle
            r=bin (means is not object (r=raw))
            l=log
        """
        if not self.types.has_key(type):
            if type=="m":
                from .SerializerMSGPack import SerializerMSGPack
                o.db.serializers.msgpack = SerializerMSGPack()
                self.types[type]=o.db.serializers.msgpack
            elif type=="c":
                from .SerializerBlosc import SerializerBlosc
                o.db.serializers.blosc = SerializerBlosc()
                self.types[type]=o.db.serializers.blosc

            elif type=="b":
                from .SerializerBlowfish import SerializerBlowfish
                self.types[type]=SerializerBlowfish(key)

            elif type=="s":
                from .SerializerSnappy import SerializerSnappy
                o.db.serializers.snappy = SerializerSnappy()
                self.types[type]=o.db.serializers.snappy

            elif type=="j":
                from .SerializerUJson import SerializerUJson
                o.db.serializers.ujson = SerializerUJson()
                self.types[type]=o.db.serializers.ujson

            elif type=="l":
                from .SerializerLZMA import SerializerLZMA
                o.db.serializers.lzma = SerializerLZMA()
                self.types[type]=o.db.serializers.lzma

            elif type=="p":
                from .SerializerPickle import SerializerPickle
                o.db.serializers.pickle = SerializerPickle()
                self.types[type]=o.db.serializers.pickle

            elif type=="6":
                self.types[type]=o.db.serializers.base64

        return self.types[type]


class Serializer():
    def __init__(self,serializationstr,key=""):
        self.serializationstr=serializationstr
        self.key=key
        for k in self.serializationstr:
            o.db.serializers.getSerializerType(k,self.key)

    def dumps(self,val):
        if self.serializationstr=="":
            return val
        for key in self.serializationstr:
            # print "dumps:%s"%key
            val=o.db.serializers.types[key].dumps(val)
        return val

    def loads(self,data):
        if self.serializationstr=="":
            return data

        for key in reversed(self.serializationstr):
            # print "loads:%s"%key
            data=o.db.serializers.types[key].loads(data)
        return data


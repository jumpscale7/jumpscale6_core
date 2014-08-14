from JumpScale import j
import JumpScale.baselib.hash
import copy


class ZDataCategorySpec():

    def __init__(self, ddict=""):
        if ddict <> "":
            self.__dict__ = ddict
        else:
            self.name = ""
            self.intId = True
            self.intIdToDisk = False
            self.sertype_disk = 12  # serialization for disk, if 0 do not store
            self.sertype_log = 12  # serialization for log, if 0 do not store
            self.process_db = ""  # process string for db
            self.process_log = False  # process string for log
            self.expiration_mem = 60 * 60  # in sec (if 0 then no cache)
            self.expiration_db = 60 * 60 * 24  # in sec
            self.expiration_log = 60 * 60 * 24 * 30  # 1month

    def setExpirationForDB(self, nr):
        """
        0 no expire, 1:1h, 2:1d, 3:1w,4:1m
        """
        t = [0, 1 * 60 * 60, 60 * 60 * 24, 60 * 60 * 24 * 7, 60 * 60 * 24 * 31]
        self.expiration_db = t[nr]

    def setExpirationForMem(self, nr):
        """
        0 no expire, 1:1h, 2:1d, 3:1w,4:1m
        """
        t = [0, 1 * 60 * 60, 60 * 60 * 24, 60 * 60 * 24 * 7, 60 * 60 * 24 * 31]
        self.expiration_mem = t[nr]

    def setExpirationForLog(self, nr):
        """
        0 no expire, 1:1h, 2:1d, 3:1w,4:1m
        """
        t = [0, 1 * 60 * 60, 60 * 60 * 24, 60 * 60 * 24 * 7, 60 * 60 * 24 * 31]
        self.expiration_log = t[nr]


class ZBase():

    def getContentKey(self):
        """
        return unique key for object, is used to define unique id

        """
        dd = copy.copy(self.__dict__)
        if dd.has_key("_ckey"):
            dd.pop("_ckey")
        if dd.has_key("id"):
            dd.pop("id")
        if dd.has_key("guid"):
            dd.pop("guid")
        if dd.has_key("sguid"):
            dd.pop("sguid")
        return j.tools.hash.md5_string(str(dd))

    def loadMessage(self, s):
        # self.__dict__.update(msgpack.loads(s))
        objecttype, objectversion, guid, obj = j.db.serializers.getSerializerType('j').loads(s)
        self.__dict__.update(obj)
        if self.guid <> "" and self.guid <> guid:
            raise RuntimeError("Data error, guid in object not same as given on serialized format")
        return (objecttype, objectversion)

    def dumpMessage(self):
        """
        to serialize to send over wire (use ujson because is fastest)
        """
        return j.db.serializers.getSerializerType('j').dumps(self._getMessage())

    def getMessage(self):
        j.errorconditionhandler.raiseBug(message="notimplemented", category=cat)

    def getCategory(self):
        j.errorconditionhandler.raiseBug(message="notimplemented", category=cat)

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


class ZRPC(ZBase):

    def __init__(self, ddict={}, cmd="", args={}):
        if ddict <> {}:
            self.__dict__ = ddict
        else:
            self.cmd = cmd
            self.args = args

    def getCategory(self):
        return "zrpc"

    def _getMessage(self):
        #[$objecttype,$objectversion,$category,$object,$id=0,$guid=""]
        return [4, self.__dict__]

from JumpScale import j
import JumpScale.baselib.hash
import copy


class OSISBaseObject():

    def init(self,ttype,version):
        self.guid=""
        self._version=version
        self._type=ttype
        self._ckey=""

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id (std the guid)
        """
        return self.guid

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes combination of other keys, std the guid and does nothing)
        """
        return self.guid

    def getContentKey(self):
        """
        is like returning the hash, is used to see if object changed
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
        for item in dd.keys():
            if item[0]=="_":
                dd.pop(item)
        return j.tools.hash.md5_string(str(dd))

    def load(self, ddict):
        """
        load the object starting from dict of primitive types (dict, list, int, bool, str, long) and a combination of those
        std behaviour is the __dict__ of the obj
        """        
        self.__dict__.update(ddict)

    def dump(self):
        """
        dump the object to a dict of primitive types (dict, list, int, bool, str, long) and a combination of those
        std behaviour is the __dict__ of the obj
        """
        return self.__dict__

    def getDictForIndex(self):
        """
        get dict of object without passwd and props starting with _
        """
        d={}
        for key,val in self.__dict__.iteritems():
            if key[0]<>"_" and key not in ["passwd","password","secret"]:
                d[key]=val
        return d
        

    def __str__(self):
        out=""
        for key,val in self.__dict__.iteritems():
            if key[0]<>"_":
                out+="%-35s :  %s\n"%(key,val)
        items=out.split("\n")
        items.sort()
        return "\n".join(items)

    __repr__ = __str__


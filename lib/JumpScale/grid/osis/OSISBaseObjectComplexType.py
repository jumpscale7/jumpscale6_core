from JumpScale import j
import JumpScale.baselib.hash
import copy

import JumpScale.baselib.code



class OSISBaseObjectComplexType(j.code.classGetJSRootModelBase()):

    def init(self,namespace,category,version):
        self.guid=j.base.idgenerator.generateGUID()
        self._ckey=""
        self._meta=[namespace,category,int(version)] #$namespace,$category,$version

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id (std the guid)
        if return None means is always unique
        """
        return None

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes combination of other keys, std the guid and does nothing)
        """
        return self.guid

    def getContentKey(self):
        """
        is like returning the hash, is used to see if object changed
        """
        dd=j.code.object2json(self,True,ignoreKeys=["guid","id","sguid","moddate"],ignoreUnderscoreKeys=True)
        return j.tools.hash.md5_string(str(dd))

    def load(self, ddict):
        """
        load the object starting from dict of primitive types (dict, list, int, bool, str, long) and a combination of those
        std behaviour is the __dict__ of the obj
        """
        j.code.dict2JSModelobject(self,ddict)

    def dump(self):
        """
        dump the object to a dict of primitive types (dict, list, int, bool, str, long) and a combination of those
        std behaviour is the __dict__ of the obj
        """
        return j.code.object2dict(self,dieOnUnknown=True)

    def getDictForIndex(self,ignoreKeys=[]):
        """
        get dict of object without passwd and props starting with _
        """
        return j.code.object2dict(self,ignoreKeys=ignoreKeys+["passwd","password","secret"],ignoreUnderscoreKeys=True)




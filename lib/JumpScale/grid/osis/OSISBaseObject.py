from JumpScale import j
import JumpScale.baselib.hash

from OSISBaseObjectComplexType import OSISBaseObjectComplexType

class OSISBaseObject(OSISBaseObjectComplexType):

    def load(self, ddict):
        """
        update object from ddict being given
        """
        self.__dict__.update(ddict)

    def __str__(self):
        return j.code.object2json(self,True)
                
    __repr__=__str__
        
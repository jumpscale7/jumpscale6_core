from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
ujson = j.db.serializers.getSerializerType('j')


class mainclass(OSISStore):

    """
    Default object implementation
    """

    def set(self, key, value, waitIndex=False):
        if j.basetype.dictionary.check(value):
            obj=self.getObject(value)
        else:
            raise RuntimeError("val should be dict in osis on set (osis_parent_vfw")
        obj.getSetGuid()
        self.db.set(self.dbprefix, key=obj.guid, value=ujson.dumps(obj.dump()))
        self.index(obj.getDictForIndex())
        return [obj.guid, True, True]



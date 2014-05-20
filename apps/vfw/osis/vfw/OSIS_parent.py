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
            raise RuntimeError("val should be dict")
        obj.getSetGuid()
        self.db.set(self.dbprefix, key=obj.guid, value=ujson.dumps(value))
        self.index(obj.getDictForIndex())
        return [obj.guid, True, True]



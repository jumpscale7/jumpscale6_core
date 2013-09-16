from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
ujson = j.db.serializers.getSerializerType('j')


class mainclass(OSISStore):

    """
    Defeault object implementation
    """

    def set(self, key, value):
        if self.db.exists(self.dbprefix, key):
            changed = True
            new = False
        else:
            changed = False
            new = True
        self.db.set(self.dbprefix, key=key, value=value)
        return [key, new, changed]


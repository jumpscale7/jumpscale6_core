from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
ujson = j.db.serializers.getSerializerType('j')


class mainclass(OSISStore):

    """
    Defeault object implementation
    """

    def set(self, key, value):
        id = value['id']
        if id and self.db.exists(self.dbprefix, id):
            orig = self.get(id)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                id = self.db.increment(self.dbprefix_incr)
                value['id'] = id
            if not value.get('guid'):
                value['guid'] = j.base.idgenerator.generateGUID()
            changed = False
            new = True
        self.db.set(self.dbprefix, key=id, value=value)
        self.index(value)
        return [id, new, changed]


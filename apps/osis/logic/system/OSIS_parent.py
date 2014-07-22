from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo
import uuid

ujson = j.db.serializers.getSerializerType('j')

class mainclass(OSISStoreMongo):
    def set(self, key, value, waitIndex=False):
        id = value.get('id')
        if id and self.exists(id):
            orig = self.get(id, True)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                id = self.incrId()
                value['id'] = id
            changed = False
            new = True
        value['guid'] = id
        self.db.save(value)
        return [id, new, changed]


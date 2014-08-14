from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo
import JumpScale.grid.grid

class mainclass(OSISStoreMongo):
    def set(self,key,value,waitIndex=True, session=None):
        dbvalue = self.db.find_one({'guid': key})
        if dbvalue is not None:
             dbvalue.update(value)
             value = dbvalue
        value['guid'] = key
	value['id'] = key
        self.db.save(value)
        return [key,True,True]

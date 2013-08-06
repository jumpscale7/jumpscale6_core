from OpenWizzy import o
from OpenWizzy.grid.osis.OSISStore import OSISStore
ujson = o.db.serializers.getSerializerType('j')


class mainclass(OSISStore):

    """
    Defeault object implementation
    """

    def set(self, key, value):
        id = value['id']
        if self.db.exists(self.dbprefix, id) and id != 0:
            orig = self.get(id)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                id = self.db.increment(self.dbprefix_incr)
                value['id'] = id
            changed = False
            new = True
        self.db.set(self.dbprefix, key=id, value=value)
        self.index(value)
        return [id, new, changed]

    def index(self, obj):
        """
        """
        obj = obj.copy()
        if self.elasticsearch <> None:
            index = self.getIndexName()
            for key5 in obj.keys():
                if key5[0] == "_":
                    obj.pop(key5)
            obj.pop("sguid", None)
            if self.indexTTL <> "":
                self.elasticsearch.index(index=index, id=str(obj['id']), doc_type=self.hrd.category_name, doc=obj, ttl=self.indexTTL, replication="async")
            else:
                self.elasticsearch.index(index=index, id=str(obj['id']), doc_type=self.hrd.category_name, doc=obj, replication="async")

    def removeFromIndex(self, key):
        index = self.getIndexName()
        result = self.elasticsearch.delete(index, self.hrd.category_name, key)
        return result

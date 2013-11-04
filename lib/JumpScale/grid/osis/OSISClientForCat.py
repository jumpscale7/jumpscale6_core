    
from JumpScale import j

json=j.db.serializers.getSerializerType("j")

class OSISClientForCat():

    def __init__(self, client, namespace, cat):
        self.namespace = namespace
        self.cat = cat
        self.client = client
        self.objectclass=None

    def _getModelClass(self):
        if self.objectclass==None:
            klass=self.client.getOsisObjectClass(self.namespace,self.cat)
            name=""
            for line in klass.split("\n"):
                if line.find("(OsisBaseObject)")<>-1 and line.find("class ")<>-1:
                    name=line.split("(")[0].lstrip("class ")
            if name=="":
                raise RuntimeError("could not find: class $modelname(OsisBaseObject) in model class file, should always be there")
            exec(klass)
            resultclass=eval(name)
            self.objectclass=resultclass

        return self.objectclass

    def new(self,**args):
        return self._getModelClass()(**args)

    def set(self, obj, key=None):
        """
        if key none then key will be given by server
        @return (guid,new,changed)
        """
        if hasattr(obj,"dump"):
            obj=obj.dump()
            guid,new,changed = self.client.set(namespace=self.namespace, categoryname=self.cat, key=key, value=obj)
            return (guid,new,changed)
        else:
            return self.client.set(namespace=self.namespace, categoryname=self.cat, key=key, value=obj)

    def get(self, key):
        value = self.client.get(namespace=self.namespace, categoryname=self.cat, key=key)
        value=json.loads(value)

        if value.has_key("_type"):
            value["_type"]
            klass=self._getModelClass()
            obj=klass()
            obj.load(value)

        return obj

    def delete(self, key):
        return self.client.delete(namespace=self.namespace, categoryname=self.cat, key=key)

    def destroy(self):
        return self.client.destroy(namespace=self.namespace, categoryname=self.cat)

    def list(self, prefix=""):
        return self.client.list(namespace=self.namespace, categoryname=self.cat, prefix=prefix)

    def search(self, query, start=0, size=None):
        return self.client.search(namespace=self.namespace, categoryname=self.cat, query=query,
                                  start=start, size=size)

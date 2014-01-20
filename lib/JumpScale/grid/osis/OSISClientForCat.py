    
from JumpScale import j

json=j.db.serializers.getSerializerType("j")

class OSISClientForCat():

    def __init__(self, client, namespace, cat):
        self.client = client
        self.namespace = namespace
        self.cat = cat
        self.objectclass=None

    def _checkCat(self):
        return  #@todo note sure I can do this?
        if self.cat not in self.client.listNamespaceCategories(self.namespace):            
            self.client.createNamespaceCategory(self.namespace, self.cat)

    def _getModelClass(self):
        self._checkCat()
        if self.objectclass==None:
            klass=self.client.getOsisObjectClass(self.namespace,self.cat)
            name=""
            for line in klass.split("\n"):
                if line.find("(OsisBaseObject)")<>-1 and line.find("class ")<>-1:
                    name=line.split("(")[0].lstrip("class ")
            if name=="":
                raise RuntimeError("could not find: class $modelname(OsisBaseObject) in model class file, should always be there")
            try:
                exec(klass)
            except Exception,e:
                from IPython import embed
                print "DEBUG NOW error in _getModelClass, OSISClientForCat"
                embed()
                
            resultclass=eval(name)
            self.objectclass=resultclass

        return self.objectclass


    def authenticate(self, name,passwd,**args):
        """
        authenticates a user and returns the groups in which the user is
        """
        self._checkCat()
        return  self.client.authenticate(namespace=self.namespace, categoryname=self.cat,name=name,passwd=passwd,**args)     

    def new(self,**args):
        self._checkCat()
        return self._getModelClass()(**args)

    def set(self, obj, key=None):
        """
        if key none then key will be given by server
        @return (guid,new,changed)
        """
        self._checkCat()
        if hasattr(obj,"dump"):
            obj=obj.dump()
            guid,new,changed = self.client.set(namespace=self.namespace, categoryname=self.cat, key=key, value=obj)
            return (guid,new,changed)
        else:
            return self.client.set(namespace=self.namespace, categoryname=self.cat, key=key, value=obj)

    def get(self, key):
        self._checkCat()
        value = self.client.get(namespace=self.namespace, categoryname=self.cat, key=key)
        if isinstance(value, basestring):
            try:
                value=json.loads(value)
            except:
                pass # might be normal string/data aswell
        if isinstance(value, dict) and value.has_key("_type"):
            value["_type"]
            klass=self._getModelClass()
            obj=klass()
            obj.load(value)
            return obj
        else:
            return value

    def exists(self, key):
            self._checkCat()
            return self.client.exists(namespace=self.namespace, categoryname=self.cat, key=key)

    def delete(self, key):
        self._checkCat()
        return self.client.delete(namespace=self.namespace, categoryname=self.cat, key=key)

    def destroy(self):
        self._checkCat()
        return self.client.destroy(namespace=self.namespace, categoryname=self.cat)

    def list(self, prefix=""):
        self._checkCat()
        return self.client.list(namespace=self.namespace, categoryname=self.cat, prefix=prefix)

    def search(self, query, start=0, size=None):
        self._checkCat()
        return self.client.search(namespace=self.namespace, categoryname=self.cat, query=query,
                                  start=start, size=size)

    def simpleSearch(self, params, start=0, size=None):
        query = {'query': {'bool': {'must': list()}}}
        myranges = {}
        for k, v in params.iteritems():
            if isinstance(v, dict):
                if not v['value']:
                    continue
                if v['name'] not in myranges:
                    myranges = {v['name']: dict()}
                myranges[v['name']] = {v['eq']: v['value']}
            elif v:
                term = {'term': {k: v}}
                query['query']['bool']['must'].append(term)
        for key, value in myranges.iteritems():
            query['query']['bool']['must'].append({'range': {key: value}})
        if not query['query']['bool']['must']:
            query = dict()
        rawresults = self.search(query, start, size)

        results = list()
        if 'result' in rawresults:
            rawresults = rawresults['result']
        elif 'hits' in rawresults:
            rawresults = rawresults['hits']['hits']
        for item in rawresults:
            results.append(item['_source'])
        return results

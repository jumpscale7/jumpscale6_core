    
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
            retcode,content=self.client.getOsisObjectClassCodeOrSpec(self.namespace,self.cat)
            if retcode==1:
                pathdir=j.system.fs.joinPaths(j.dirs.varDir,"code","osis",self.namespace)
                path=j.system.fs.joinPaths(pathdir,"model.spec")
                j.system.fs.createDir(pathdir)
                j.system.fs.writeFile(filename=path,contents=content)                
                resultclass=j.core.osis.getOsisModelClass(self.namespace,self.cat,specpath=path)
                self.objectclass=resultclass
            elif retcode==2:
                klass=content
                name=""
                for line in klass.split("\n"):
                    if line.find("(OsisBaseObject)")<>-1 and line.find("class ")<>-1:
                        name=line.split("(")[0].lstrip("class ")
                if name=="":
                    raise RuntimeError("could not find: class $modelname(OsisBaseObject) in model class file, should always be there")
                try:
                    exec(klass)
                except Exception,e:
                    raise RuntimeError("Could not import osis: %s_%s error:%s"%(self.namespace,self.cat,e))
                
                resultclass=eval(name)
                self.objectclass=resultclass
            else:
                raise RuntimeError("Could not find spec or class code for %s_%s on osis"%(self.namespace,self.cat))

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

    def simpleSearch(self, params, start=0, size=None, withguid=False, withtotal=False, sort=None, partials=None, nativequery=None):
        if nativequery:
            query = nativequery.copy()
        else:
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
        if partials:
            query['query']['bool']['must'].append({'wildcard': partials})
        boolq = query['query']['bool']
        def isEmpty(inputquery):
            for key, value in inputquery.iteritems():
                if value:
                    return False
            return True

        if isEmpty(boolq):
            query = dict()
        if sort:
            query['sort'] = [ {x:v} for x,v in sort.iteritems() ]

        response = self.search(query, start, size)

        results = list()
        if 'result' in response:
            rawresults = response['result']
        elif 'hits' in response:
            rawresults = response['hits']['hits']
        for item in rawresults:
            if withguid:
                item['_source']['guid'] = item['_id']
            results.append(item['_source'])
        if not withtotal:
            return results
        else:
            total = -1
            if 'total' in response:
                total = response['total']
            elif 'hits' in response and 'total' in response['hits']:
                total = response['hits']['total']
            return total, results

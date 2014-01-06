from JumpScale import j
import copy
json=j.db.serializers.getSerializerType("j")
import imp

class OSISStore(object):

    """
    Default object implementation (is for one specific namespace_category)
    """

    def init(self, path, namespace,categoryname):

        self.path = path
        self.tasklets = {}

        # for tasklettype in j.system.fs.listDirsInDir(self.path, dirNameOnly=True):
        #     self.tasklets[tasklettype] = j.core.taskletengine.get(j.system.fs.joinPaths(self.path, tasklettype))

        self.db = None

        self.db = self._getDB()

        self.namespace = namespace
        self.categoryname = categoryname

        if self.namespace=="" or self.categoryname=="":
            raise RuntimeError("namespace & category cannot be empty")

        self.dbprefix = "%s_%s" % (self.namespace, self.categoryname)
        self.dbprefix_incr = "%s_incr" % (self.dbprefix)

        self.buildlist = False

        self.elasticsearch = self._getElasticSearch()
        status = self.elasticsearch.status()
        indexname = self.getIndexName()
        if indexname not in status['indices'].keys():
            import pyelasticsearch
            try:
                self.elasticsearch.create_index(self.getIndexName())
            except pyelasticsearch.IndexAlreadyExistsError:
                pass 

        # if self.tasklets.has_key("init"):
        #     self.tasklets["init"].executeV2(osis=self)

        self.objectclass=None

        authpath=j.system.fs.joinPaths(self.path,"OSIS_auth.py")
        auth=None
        authparent=None
        if j.system.fs.exists(authpath):
            testmod = imp.load_source("auth_%s"%self.dbprefix, authpath)
            auth=testmod.AUTH()
            auth.load(self)

        authpath=j.system.fs.joinPaths(j.system.fs.getParent(self.path),"OSIS_auth.py")
        if j.system.fs.exists(authpath):
            testmod = imp.load_source("auth_%s"%self.dbprefix, authpath)
            authparent=testmod.AUTH()
            authparent.load(self)

        self.auth=auth
        if self.auth==None and authparent<>None:
            self.auth=authparent

    def _getModelClass(self):
        if self.objectclass==None:

            path=j.system.fs.joinPaths(self.path, "model.py")
            if j.system.fs.exists(path):
                klass= j.system.fs.fileGetContents(path)
            else:
                self.objectclass= ""
                # raise RuntimeError("Cannot find class for %s"%self.dbprefix)

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

    def _getDB(self):
        if j.core.osis.db == None:
            j.errorconditionhandler.raiseBug(message="osis needs to have a temp db connection", category="osis.init")
        return j.core.osis.db

    def _getElasticSearch(self):
        if j.core.osis.elasticsearch == None:
            j.errorconditionhandler.raiseBug(message="osis needs to have a temp db connection", category="osis.init")
        return j.core.osis.elasticsearch

    def get(self, key):
        """
        get dict value
        """
        return self.db.get(self.dbprefix, key)

    def exists(self, key):
        """
        get dict value
        """
        return self.db.exists(self.dbprefix, key)


    def getObject(self, ddict={}):
        klass=self._getModelClass()
        if klass=="":
            return ddict            
        obj = klass(ddict=ddict)
        return obj

    def set(self, key, value):
        obj = self.getObject(value)

        self.db.set(self.dbprefix, key=obj.guid, value=value)

        if obj<>value:
            #means there is a model found
            self.index(obj)

        return [None, None, None]

    def getIndexName(self):
        """
        return name of index in elastic search, depends on properies of object
        """
        return self.dbprefix

    def index(self, obj,ttl=0):
        """
        @param ttl = time to live in seconds of the index
        """
        obj = copy.copy(obj)
        if self.elasticsearch == None:
            raise RuntimeError("Cannot find index")

        index = self.getIndexName()

        if j.basetype.dictionary.check(obj):
            data=obj
        else:
            data=obj.__dict__
        guid=data["guid"]
        data.pop("guid")  # remove guid from object before serializing to json
        for key5 in data.keys():
            if key5[0] == "_":
                data.pop(key5)
        try:
            data.pop("sguid")
        except:
            pass
        
        try:
            if ttl <> 0:
                self.elasticsearch.index(index=index, id=guid, doc_type="json", doc=data, ttl=ttl, replication="async")
            else:
                self.elasticsearch.index(index=index, id=guid, doc_type="json", doc=data, replication="async")
        except Exception,e:
            if str(e).find("Index failed")<>-1:
                try:
                    msg="cannot index object:\n%s"%obj
                except Exception,ee:
                    msg="cannot index object, cannot even print object"                
                print e
                j.errorconditionhandler.raiseOperationalCritical(msg, category='osis.index', msgpub='', die=True, tags='', eco=None)
            else:
                j.errorconditionhandler.processErrorConditionObject(j.errorconditionhandler.parsePythonErrorObject(e))
            

    def exists(self, key):
        return self.db.exists(self.dbprefix, key)

    def delete(self, key):
        self.db.delete(self.dbprefix, key)
        self.removeFromIndex(key)

    def removeFromIndex(self, key):
        index = self.getIndexName()
        result = self.elasticsearch.delete(index, 'json', key)
        return result

    def find(self, query, start=0, size=None):
        if not isinstance(query, dict):
            query = json.loads(query)
        
        index = self.getIndexName()
        if size:
            result = self.elasticsearch.search(query=query, index=index, es_from=start,
                                           size=size)
        else:
            result = self.elasticsearch.search(query=query, index=index, es_from=0, size=100000)
        if not isinstance(result, dict):
            result = result()
        return {'result': result['hits']['hits'],
                'total': result['hits']['total']}

    def destroyindex(self):
        if len(self.categoryname) < 4:
            j.errorconditionhandler.raiseBug(message="osis categoryname needs to be at least 3 chars.", category="osis.bug")
        indexes = self.elasticsearch.get_mapping().keys()
        for i in indexes:
            if i.find(self.categoryname) == 0:
                self.elasticsearch.delete_index(i)

    def destroy(self):
        """
        delete objects as well as index (all)
        """
        self.destroyindex()
        
        self.db.destroy(category=self.dbprefix)
        self.db.destroy(category=self.dbprefix_incr)
        self.db.incrementReset(self.dbprefix_incr)

    def list(self, prefix="", withcontent=False):
        """
        return all object id's stored in DB
        """
        db = self.db

        if withcontent == False:
            return db.list(self.dbprefix, prefix)

    def rebuildindex(self):
        #@todo push to worker, this will be too slow (best to create sort of mapreduce alike technique)
        self.destroyindex()
        ids = self.list()
        for id in ids:
            obj = self.get(id)
            self.index(obj)


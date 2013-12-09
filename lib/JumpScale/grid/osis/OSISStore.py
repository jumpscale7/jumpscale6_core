from JumpScale import j
import copy
json=j.db.serializers.getSerializerType("j")


class OSISStore(object):

    """
    Default object implementation (is for one specific namespace_category)
    """

    def init(self, path, hrd):

        self.path = path
        self.hrd = hrd
        self.tasklets = {}

        for tasklettype in j.system.fs.listDirsInDir(self.path, dirNameOnly=True):
            self.tasklets[tasklettype] = j.core.taskletengine.get(j.system.fs.joinPaths(self.path, tasklettype))

        self.db = None

        self.db = self._getDB()

        self.namespace = self.hrd.get("namespace.name")
        self.categoryname = self.hrd.get("category.name")

        if self.namespace=="" or self.categoryname=="":
            raise RuntimeError("namespace & category cannot be empty")

        self.dbprefix = "%s_%s" % (self.namespace, self.categoryname)
        self.dbprefix_incr = "%s_incr" % (self.dbprefix)

        indexEnabled = self.hrd.getInt("category.index") == 1
        elasticsearchEnabled = self.hrd.getInt("category.elasticsearch") == 1

        self.buildlist = False

        if elasticsearchEnabled:
        # put on None if no elastic search
            self.elasticsearch = self._getElasticSearch()
            status = self.elasticsearch.status()
            indexname = self.getIndexName()
            if indexname not in status['indices'].keys():
                import pyelasticsearch
                try:
                    self.elasticsearch.create_index(self.getIndexName())
                except pyelasticsearch.IndexAlreadyExistsError:
                    pass # we pass this cause elasticsearch can have some delays
        else:
            self.elasticsearch = None
            if indexEnabled:
                self.buildlist = True

        if self.tasklets.has_key("init"):
            self.tasklets["init"].executeV2(osis=self)

        self.indexTTL = self.hrd.get("category.indexttl")

        self.objectclass=None

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

    def getObject(self, ddict={}):
        klass=self._getModelClass()
        if klass=="":
            return ddict            
        obj = klass(ddict=ddict)
        return obj

    def set(self, key, value):
        obj = self.getObject(value)

        if self.tasklets.has_key("set_pre"):
            from IPython import embed
            print "DEBUG NOW setpre tasklets"
            embed()
            
            self.tasklets["set_pre"].executeV2()

        self.db.set(self.dbprefix, key=obj.guid, value=value)

        if self.tasklets.has_key("set_post"):
            from IPython import embed
            print "DEBUG NOW set_post tasklets"
            embed()
            self.tasklets["set_post"].executeV2()

        if obj<>value:
            #means there is a model found
            self.index(obj)

        return [None, None, None]

    def getIndexName(self):
        """
        return name of index in elastic search, depends on properies of object
        """
        return self.dbprefix

    def index(self, obj):
        """
        """
        obj = copy.copy(obj)
        if self.elasticsearch <> None:
            index = self.getIndexName()

            guid = obj.guid
            obj.__dict__.pop("guid")  # remove guid from object before serializing to json
            for key5 in obj.__dict__.keys():
                if key5[0] == "_":
                    obj.__dict__.pop(key5)
            try:
                obj.__dict__.pop("sguid")
            except:
                pass
            data = obj.__dict__
            
            if self.indexTTL <> "":
                self.elasticsearch.index(index=index, id=guid, doc_type="json", doc=data, ttl=self.indexTTL, replication="async")
            else:
                self.elasticsearch.index(index=index, id=guid, doc_type="json", doc=data, replication="async")

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


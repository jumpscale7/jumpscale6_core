from OpenWizzy import o
import copy, json
class OSISStore(object):
    """
    Defeault object implementation
    """
    def init(self,path,hrd):

        self.path=path
        self.hrd=hrd
        self.tasklets={}

        for tasklettype in o.system.fs.listDirsInDir(self.path,dirNameOnly=True):
            self.tasklets[tasklettype]=o.core.taskletengine.get(o.system.fs.joinPaths(self.path,tasklettype))

        self.db=None
        
        self.db=self._getDB()

        self.dbprefix="%s_%s"%(self.hrd.getInt("namespace.id"),self.hrd.getInt("category.id"))
        self.dbprefix_incr="%s_incr"%(self.dbprefix)
        # self.namespace=str(self.hrd.getInt("namespace.id"))
        # self.category=str(self.hrd.getInt("category.id"))
        self.categoryname=self.hrd.get("category.name")

        indexEnabled=self.hrd.getInt("category.index")==1
        elasticsearchEnabled=self.hrd.getInt("category.elasticsearch")==1

        self.buildlist=False

        if elasticsearchEnabled:
        #put on None if no elastic search
            self.elasticsearch=self._getElasticSearch()
            from elasticsearch import pyelasticsearch
            try:
                self.elasticsearch.create_index(self.getIndexName())
            except pyelasticsearch.IndexAlreadyExistsError:
                pass
        else:
            self.elasticsearch=None
            if indexEnabled:
                self.buildlist=True

        if self.tasklets.has_key("init"):
            self.tasklets["init"].executeV2(osis=self)

        self.indexTTL=self.hrd.get("category.indexttl")

    def _getDB(self):
        if o.core.osis.db==None:
            o.errorconditionhandler.raiseBug(message="osis needs to have a temp db connection",category="osis.init")
        return o.core.osis.db

    def _getElasticSearch(self):
        if o.core.osis.elasticsearch==None:
            o.errorconditionhandler.raiseBug(message="osis needs to have a temp db connection",category="osis.init")
        return o.core.osis.elasticsearch

    def get(self,key):
        """
        get dict value
        """
        return self.db.get(self.dbprefix,key)

    def getObject(self,ddict={}):
        obj=o.core.grid.zobjects.getZNodeObject(ddict=ddict)
        return obj

    def set(self,key,value):
        obj=self.getObject(value)
        if self.db.exists(self.dbprefix_incr, obj.guid):
            changed = True
            new = False
        else:
            changed = False
            new = True
        value = obj.__dict__
        self.db.set(self.dbprefix,key=obj.guid,value=value)
        self.index(obj)
        return [obj.guid,new,changed]

    def getIndexName(self):
        """
        return name of index in elastic search, depends on properies of object
        """
        index = '%s_%s' % (self.hrd.category_name, self.hrd.namespace_id)
        return index 

    def index(self,obj):
        """
        """
        obj=copy.copy(obj)
        if self.elasticsearch<>None:
            index=self.getIndexName()

            guid=obj.guid
            obj.__dict__.pop("guid") #remove guid from object before serializing to json
            for key5 in obj.__dict__.keys():
                if key5[0]=="_":
                    obj.__dict__.pop(key5)
            try:
                obj.__dict__.pop("sguid")
            except:
                pass
            data=obj.__dict__
            if self.indexTTL<>"":
                self.elasticsearch.index(index=index,id=guid,doc_type="json",doc=data,ttl=self.indexTTL,replication="async")
            else:
                self.elasticsearch.index(index=index,id=guid,doc_type="json",doc=data,replication="async")

    def exists(self,key):
        return self.db.exists(self.dbprefix, key)

    def delete(self,key):
        self.db.delete(self.dbprefix, key)
        self.removeFromIndex(key)

    def removeFromIndex(self,key):
        index = self.getIndexName() 
        result = self.elasticsearch.delete(index, 'json', key)
        return result

    def find(self,query, start = 0, size = 10):
        query  = json.loads(query)
        index = '%s_%s' % (self.hrd.category_name, self.hrd.namespace_id)
        result = self.elasticsearch.search(query=query, index=index, es_from=start,
                size=size)()
        return {'result': result['hits']['hits'],
                'total':result['hits']['total']}

    def destroyindex(self):
        if len(self.categoryname)<4:
            o.errorconditionhandler.raiseBug(message="osis categoryname needs to be at least 3 chars.",category="osis.bug")
        indexes=self.elasticsearch.get_mapping().keys()
        for i in indexes:
            if i.find(self.categoryname)==0: 
                self.elasticsearch.delete_index(i)

    def destroy(self):
        """
        delete objects as well as index (all)
        """
        self.destroyindex()
        self.db.destroy(category=self.dbprefix)
        self.db.destroy(category=self.dbprefix_incr)
        self.db.incrementReset(self.dbprefix_incr)

    def list(self,prefix="",withcontent=False):
        """
        return all object id's stored in DB
        """
        db=self.db

        if withcontent==False:
            return db.list(self.dbprefix,prefix)

    def rebuildindex(self):
        #@todo push to worker, this will be too slow (best to create sort of mapreduce alike technique)
        self.destroyindex()
        ids=self.list()
        for id in ids:
            obj=self.get(id)
            self.index(obj)

    def serialize(self,obj):
        return o.db.serializers.ujson.dumps(obj)

    def unserialize(self,obj):
        return o.db.serializers.ujson.loads(obj)
            


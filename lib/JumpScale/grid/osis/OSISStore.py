from JumpScale import j
import copy
import imp
# import ujson as json

class OSISStore(object):
    """
    Default object implementation (is for one specific namespace_category)
    """

    def __init__(self):
        pass
        

    def init(self, path, namespace,categoryname):
        """
        gets executed when catgory in osis gets loaded by osiscmds.py (.init method)
        """
        self.json=j.db.serializers.getSerializerType("j")

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

    # def _getModelClass(self):
    #     """
    #     is called when someone needs an object
    #     """
    #     if self.objectclass==None:

    #         #need to check if there is a specfile or we go from model.py
    #         specpath=j.system.fs.joinPaths(self.path, "model.spec")    
    #         print "SPECPATH:%s" %specpath
    #         if j.system.fs.exists(path=specpath):
    #             j.core.specparser.parseSpecs(self.path, appname=self.categoryname, actorname="osismodel")
    #             spec = j.core.specparser.getActorSpec(appname, actorname, raiseError=False)            
    #             from IPython import embed
    #             print "DEBUG NOW uuuuu"
    #             embed()
                
    #         path=j.system.fs.joinPaths(self.path, "model.py")
    #         if j.system.fs.exists(path):
    #             klass= j.system.fs.fileGetContents(path)
    #         else:
    #             self.objectclass= ""
    #             # raise RuntimeError("Cannot find class for %s"%self.dbprefix)

    #         name=""

    #         for line in klass.split("\n"):
    #             if line.find("(OsisBaseObject)")<>-1 and line.find("class ")<>-1:
    #                 name=line.split("(")[0].lstrip("class ")
    #         if name=="":
    #             raise RuntimeError("could not find: class $modelname(OsisBaseObject) in model class file, should always be there.\nClass file on %s"%)
    #         exec(klass)
    #         resultclass=eval(name)
    #         self.objectclass=resultclass

    #     return self.objectclass

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
        klass=j.core.osis.getOsisModelClass(self.namespace,self.categoryname)
        if klass=="":
            return ddict            
        obj = klass(ddict=ddict)
        return obj

    def setObjIds(self,obj):
        """
        for osis object get unique id & set it in object
        return (new,changed,obj) #new & changed=boolean
        """        
        ckey=obj.getContentKey()
        # print "ckey:%s"%ckey
        ukey=obj.getUniqueKey()
        # print "ukey:%s"%ukey
        if ukey==None or str(ukey)=="":
            # print "UKEY NONE SO NEW"
            changed=True
            new=True
            ukey=None
        else:
            changed=False
            new=False
        
        if ukey<>None and self.db.exists(self.dbprefix_incr, ukey):
            # print "ukey exists"
            new=False            
            id,guid,ckey2=self.json.loads(self.db.get(self.dbprefix_incr, ukey))
            guid=str(guid)
            ckey=str(ckey)
            ckey2=str(ckey2)
            # print "guid,ckey in db: %s:%s"%(guid,ckey2)
            if obj.id<>id:
                obj.id=id
            obj.getSetGuid()
            if obj.guid<>guid:
                # print "GUID changed"
                changed=True
            ckey=obj.getContentKey()
            if ckey2<>ckey:
                # print "content changed"
                changed=True
            if changed:
                json=self.json.dumps([obj.id,obj.guid,ckey])
                self.db.set(self.dbprefix_incr, ukey, json)       
            # print "ret:%s %s" %(new,changed)         
            return (new,changed,obj)
        else:
            # print "ukey not in db"
            new=True
            changed=True    
            if not hasattr(obj, 'id') or not obj.id:
                id=self.db.increment(self.dbprefix_incr)
                # print "newid:%s"%id
                obj.id=id
            obj.getSetGuid()
            ukey=obj.getUniqueKey()
            ckey=obj.getContentKey()
            obj._ckey=ckey
            # print "ukey,ckey for new object: %s:%s"%(ukey,ckey)
            if ukey<>None:
                json=self.json.dumps([obj.id,obj.guid,ckey])
                self.db.set(self.dbprefix_incr, ukey, json)
            return (new,changed,obj)

    def set(self, key, value):
        """
        value can be a dict or a raw value (seen as string)
        if raw value then will not try to index
        """
        if j.basetype.dictionary.check(value):
            #is probably an osis object
            obj=self.getObject(value)
            if not j.basetype.dictionary.check(obj):
                new,changed,obj=self.setObjIds(obj)
                key=obj.guid
                self.index(obj)
                value=self.json.dumps(obj.obj2dict())
            else:
                value=self.json.dumps(value)
                new=None
                changed=None
        else:
            new=True
            changed=True
            from IPython import embed
            print "DEBUG NOW osisstoreset should be dict"
            embed()
            
        
        #not an osis obj, need to stor as raw value, there will be no indexing
        self.db.set(self.dbprefix, key=key, value=value)
        return (key,new,changed)

    def getIndexName(self):
        """
        return name of index in elastic search, depends on properies of object
        """
        return self.dbprefix

    def index(self, obj,ttl=0):
        """
        @param ttl = time to live in seconds of the index
        """
        if self.elasticsearch == None:
            raise RuntimeError("Cannot find index")

        index = self.getIndexName()

        if j.basetype.dictionary.check(obj):
            data=copy.copy(obj)
            data=obj
        else:
            if hasattr(obj,"getDictForIndex"):
                data=obj.getDictForIndex()
            else:
                if isinstance(obj, basestring):
                    obj = self.json.loads(obj)
                    data=copy.copy(obj)
                else:
                    data=copy.copy(obj.__dict__)

        guid=data["guid"]

        # data.pop("guid")  # remove guid from object before serializing to json
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
                    msg="cannot index object:\n%s"%data
                except Exception,ee:
                    msg="cannot index object, cannot even print object"                
                print e
                j.errorconditionhandler.raiseOperationalCritical(msg, category='osis.index', msgpub='', die=False, tags='', eco=None)
            elif str(e).find("failed to parse")<>-1:
                try:
                    msg="indexer cannot parse object (normally means 1 or more subtypes of doc was changed)"
                except Exception,ee:
                    msg="indexer cannot parse object, cannot even print object.\n%s"%ee
                    j.errorconditionhandler.raiseOperationalCritical(msg, category='osis.index.parse', msgpub='', die=False, tags='', eco=None)
                    return
                j.errorconditionhandler.raiseOperationalCritical(msg, category='osis.index.parse', msgpub='', die=False, tags='', eco=None,extra=data)
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
            query = self.json.loads(query)
        
        index = self.getIndexName()
        size = size or 100000

        try:
            result = self.elasticsearch.search(query=query, index=index, es_from=start,
                                           size=size)
        except:
            result = {'hits': {'hits': list(), 'total': 0}}
        if not isinstance(result, dict):
            result = result()
        return {'result': result['hits']['hits'],
                'total': result['hits']['total']}

    def destroyindex(self):
        if len(self.categoryname) < 4:
            j.errorconditionhandler.raiseBug(message="osis categoryname needs to be at least 3 chars.", category="osis.bug")
        indexes = self.elasticsearch.get_mapping().keys()
        for i in indexes:
            if i.find(self.dbprefix) == 0:
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

    def export(self, outputpath):
        """
        export all objects of a category to json format.
        Placed in outputpath
        """
        if not j.system.fs.isDir(outputpath):
            j.system.fs.createDir(outputpath)
        ids = self.list()
        for id in ids:
            obj = self.get(id)
            filename = j.system.fs.joinPaths(outputpath, id)
            j.system.fs.writeFile(filename, obj)
            


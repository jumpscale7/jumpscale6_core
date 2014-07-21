from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
# ujson = j.db.serializers.getSerializerType('j')
import imp
import ujson as json
import pymongo
from pymongo import MongoClient
import JumpScale.baselib.redisworker
import JumpScale.grid.mongodbclient
import time

class OSISStoreMongo(OSISStore):
    MULTIGRID = True

    """
    Default object implementation for mongodbserver
    NEW: 
    - powerfull search capabilities
    - more consistent way of working with id's & guid's

    """

    def _getDB(self):
        raise RuntimeError("Not Implemented")

    def init(self, path, namespace, categoryname):
        """
        gets executed when catgory in osis gets loaded by osiscmds.py (.init method)
        """
        self.initall(path, namespace, categoryname, db=False)
        config = j.application.config
        host = config.get('mongodb.host') if config.exists('mongodb.host') else 'localhost'
        port = config.getInt('mongodb.port') if config.exists('mongodb.port') else 27017
        mongodb_client = j.clients.mongodb.get(host, port)

        if self.MULTIGRID:
            self.db = mongodb_client[namespace]
        else:
            dbnamespace = '%s_%s' % (j.application.whoAmI.gid, namespace)
            self.db = mongodb_client[dbnamespace]
        self.client = self.db[categoryname]
        self.counter = self.db["counter"]

        seq= {"_id": categoryname, "seq": 0}
        if self.counter.find_one({'_id': categoryname}) == None:
            self.counter.save(seq)

    def _getObjectId(self, id):
        return pymongo.mongo_client.helpers.bson.objectid.ObjectId(id)

    def incrId(self):
        self.counter.update({'_id': self.categoryname},{"$inc": {"seq": 1}})
        seq = self.counter.find_one({'_id': self.categoryname})
        return seq["seq"]

    def setPreSave(self, value):
        return value

    def set(self, key, value,**args):
        """
        value can be a dict or a raw value (seen as string)
        """
        if j.basetype.dictionary.check(value):
            objInDB=None

            if value.has_key("id") and int(value["id"])<>0:                
                objInDB=self.client.find_one({"id":value["id"]}) 

            elif value.has_key("guid") and value["guid"]<>"":                
                value["guid"]=value["guid"].replace("-","")
                objInDB=self.client.find_one({"guid":value["guid"]}) 

            if objInDB<>None:
                # value["_id"]=
                # value.pop("guid")

                objInDB.update(value)
                # objInDB.pop("guid")
                objInDB["guid"]=objInDB["guid"].replace("-","")
                objInDB = self.setPreSave(objInDB)
                self.client.save(objInDB)
                new=False
                return (new,True,objInDB["guid"])
            
            new=True
            value["guid"]=value["guid"].replace("-","")
            if value.has_key("id") and int(value["id"])==0:
                value["id"]=self.incrId()

            value = self.setPreSave(value)

            self.client.save(value)
            return (new,True,value["guid"])
        else:
            raise RuntimeError("value can only be dict")

    def get(self, key, full=False):
        if j.basetype.string.check(key):
            key=key.replace("-","")
            res=self.client.find_one({"guid":key})
        else:
            res=self.client.find_one({"id":key})

        # res["guid"]=str(res["_id"])
        if res<>None:
            if not full:
                res.pop("_id")
        return res
        
    def exists(self, key):
        """
        get dict value
        """
        # oid=pymongo.mongo_client.helpers.bson.objectid.ObjectId(key)
        if j.basetype.string.check(key):
            return not self.client.find_one({"guid":key})==None
        else:
            return not self.client.find_one({"id":key})==None

    def index(self, obj,ttl=0,replication="sync",consistency="all",refresh=True):
        #NOT RELEVANT FOR THIS TYPE OF DB
        return

    def delete(self, key):
        if j.basetype.string.check(key):
            key=key.replace("-","")
            res=self.client.find_one({"guid":key})
        else:
            res=self.client.find_one({"id":key})
        if res<>None:
            self.client.remove(res["_id"])
        
    def deleteIndex(self, key,waitIndex=False,timeout=1):           
        #NOT RELEVANT FOR THIS TYPE OF DB
        pass

    def removeFromIndex(self, key,replication="sync",consistency="all",refresh=True):
        #NOT RELEVANT FOR THIS TYPE OF DB
        pass

    def find(self, query, start=0, size=200):  
        """
        query can be a dict or a string

        when a dict
        @todo describe

        when a string
        query is tag based format with some special keywords

        generic format:  $fieldname:$filter

        special keywords
        - @sort     : comma separated list of fields to sort on
        - @start    : int starting from 0
        - @size     : nr of records to show
        - @fields   : comma separated list of fields to show

        :$filter is
        - absolute value (so the full field)
        - *something*  * is any str
        - time based argument (see below)
        - <10 or >10  (10 is any int)

        example

        'company:acompany creationdate:>-5m nremployees:<4'
        this query would be companies created during last 5 months with less than 4 employees

        special keys for time based search (only relevant for epoch fields):
          only supported now is -3m, -3d and -3h  (ofcourse 3 can be any int)
          and an int which would be just be returned
          means 3 days ago 3 hours ago
          if 0 or '' then is now
          also ok is +3m, ... (+ is for future)
          (is using j.base.time.getEpochAgo & getEpochFuture)



        """      
        if size==None:
            size=200
        sortlist=[]
        if j.basetype.string.check(query):
            tags=j.core.tags.getObject(query)
            sort=None
            if tags.tagExists("@sort"):
                sort=tags.tagGet("@sort")
                tags.tagDelete("@sort")
                for item in sort.split(","):
                    item=item.strip()
                    if item=="":
                        continue
                    if item[0]=="-":
                        item=item.strip("-")
                        sortlist.append((item,-1))
                    else:
                        sortlist.append((item,1))


            if tags.tagExists("@size"):
                size=int(tags.tagGet("@size"))
                tags.tagDelete("@size")

            if tags.tagExists("@start"):
                start=int(tags.tagGet("@start"))
                tags.tagDelete("@start")            

            fields=None
            if tags.tagExists("@fields"):
                fields=tags.tagGet("@fields")
                tags.tagDelete("@fields")
                fields=[item.strip() for item in fields.split(",") if item.strip()<>""]

            params=tags.getDict()
            for key, value in params.copy().iteritems():
                if value.startswith('>'):
                    if 'm' in value or 'd' in value or 'h' in value:
                        new_value = j.base.time.getEpochAgo(value[1:])
                    else:
                        new_value = j.basetype.float.fromString(value[1:])
                    params[key] = {'$gte': new_value}
                elif value.startswith('<'):
                    if 'm' in value or 'd' in value or 'h' in value:
                        new_value = j.base.time.getEpochFuture(value[1:])
                    else:
                        new_value = j.basetype.float.fromString(value[1:])
                    params[key] = {'$lte': new_value}
                elif '*' in value:
                    params[key] = {'$regex': '.*%s.*' % value.replace('*', '')}

            result=[]
            for item in self.client.find(params,limit=size,skip=start,fields=fields,sort=sortlist):
                item.pop("_id")
                result.append(item)
            return result
        else:
            mongoquery = dict()
            if 'query' in query:
                query.setdefault('query', {'bool':{'must':{}}})
                query['query']['bool'].setdefault('should', {})
                query['query']['bool'].setdefault('must', {})
                for queryitem in query['query']['bool']['must']:
                    if 'term' in queryitem:
                        for k, v in queryitem['term'].iteritems():
                            mongoquery[k] = v
                    if 'range' in queryitem:
                        for k, v in queryitem['range'].iteritems():
                            operatormap = {'from':'$gte', 'to':'$lte'}
                            for operator, val in v.iteritems():
                                mongoquery[k] = {operatormap[operator]: val}
                    if 'wildcard' in queryitem:
                        for k, v in queryitem['wildcard'].iteritems():
                            mongoquery[k] = {'$regex': '.*%s.*' % str(v).replace('*', '')}
                    if 'terms' in queryitem:
                        for k, v in queryitem['terms'].iteritems():
                            mongoquery[k] = {'$in': v}

                wilds = dict()
                mongoquery['$or'] = list()
                for queryitem in query['query']['bool']['should']:
                    if 'wildcard' in queryitem:
                        for k, v in queryitem['wildcard'].iteritems():
                            wilds[k] = {'$regex': '.*%s.*' % str(v).replace('*', '')}
                            mongoquery['$or'].append(wilds)

                if not mongoquery['$or']:
                    mongoquery.pop('$or')
            else:
                mongoquery = query
            start = int(start)
            size = int(size)
            if 'sort' in query:
                sorting = list()
                for field in query['sort']:
                    sorting.append((field.keys()[0], 1 if field.values()[0] == 'asc' else -1))
                mongoquery.pop('sort')
                resultdata = self.client.find(mongoquery).sort(sorting).skip(start).limit(size)
            else:
                resultdata = self.client.find(mongoquery).skip(start).limit(size)

            count = self.client.find(mongoquery).count()
            result = [count, ]
            for item in resultdata:
                item.pop("_id")
                result.append(item)
            return result

    def destroyindex(self):
        self.client.drop()

    def deleteSearch(self,query):
        if not j.basetype.string.check(update):
            raise RuntimeError("not implemented")
        query+=' @fields:guid'
        counter=0
        for item in self.find(query=query):
            self.delete(item["guid"])
            counter+=1
        return counter
        
    def updateSearch(self,query,update):
        """
        update is dict or text
        dict e.g. {"name":aname,nr:1}  these fields will be updated then
        text e.g. name:aname nr:1
        """
        if not j.basetype.string.check(query):
            raise RuntimeError("not implemented")
        if j.basetype.string.check(update):
            tags=j.core.tags.getObject(update)
            update=tags.getDict()            
        # self.client.find_and_modify(query,update=update)
        query+=' @fields:guid'
        counter=0
        for item in self.find(query=query):
            update["guid"]=item["guid"]
            self.set(value=update)
            counter+=1
            
        return counter

    def destroy(self):
        """
        delete objects as well as index (all)
        """
        self.client.drop()
        self.rebuildindex()

    def demodata(self):
        path=j.system.fs.joinPaths(self.path,"demodata.py")
        if j.system.fs.exists(path):
            module = imp.load_source("%s_%s_demodata"%(self.namespace,self.categoryname), path)    
            job=j.clients.redisworker.execFunction(module.populate,_organization=self.namespace,_category=self.categoryname,_timeout=60,_queue="io",_log=True,_sync=False)

    def list(self, prefix="", withcontent=False):
        """
        return all object id's stored in DB
        """
        result = list()
        if withcontent:
            cursor = self.client.find()
            for item in cursor:
                item.pop('_id')
                result.append(item)
        else:
            cursor = self.client.find(fields=['id',])
            for item in cursor:
                result.append(item['id'])
        return result

    def rebuildindex(self):
        path=j.system.fs.joinPaths(self.path,"index.py")
        if j.system.fs.exists(path):
            module = imp.load_source("%s_%sindex"%(self.namespace,self.categoryname), path)
            module.index(self.client)

    def export(self, outputpath,query=""):
        """
        export all objects of a category to json format, optional query
        Placed in outputpath
        """
        if not j.system.fs.isDir(outputpath):
            j.system.fs.createDir(outputpath)
        ids = self.list()
        for id in ids:
            obj = self.get(id)
            filename = j.system.fs.joinPaths(outputpath, id)
            if isinstance(obj, dict):
                obj = json.dumps(obj)
            j.system.fs.writeFile(filename, obj)

    def importFromPath(self, path):
        '''Imports OSIS category from file system'''
        if not j.system.fs.exists(path):
            raise RuntimeError("Can't find the specified path: %s" % path)

        data_files = j.system.fs.listFilesInDir(path)
        for data_file in data_files:
            with open(data_file) as f:
                obj = json.load(f)
            self.set(obj['id'], obj)

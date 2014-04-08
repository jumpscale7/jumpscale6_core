from JumpScale import j
import copy
import imp
import ujson as json
import time
#is osisstor for elasticsearch only

from OSISStore import OSISStore

class OSISStoreES(OSISStore):
    """
    Default object implementation (is for one specific namespace_category)
    """
    def init(self, path, namespace,categoryname):
        """
        gets executed when catgory in osis gets loaded by osiscmds.py (.init method)
        """
        self.initall(path, namespace,categoryname,db=False)

    def set(self, key, value,waitIndex=False):
        """
        value can be a dict or a raw value (seen as string)
        if raw value then will not try to index
        """
        if j.basetype.dictionary.check(value):
            #is probably an osis object
            obj=self.getObject(value)
            if not j.basetype.dictionary.check(obj):
                obj.getSetGuid()
                key=obj.guid
                if waitIndex:#need to make sure is out first
                    if self.existsIndex(key=key):
                        self.deleteIndex(key=key,waitIndex=True)
                self.index(obj)
                if waitIndex:
                    time.sleep(0.2)
                    if not self.existsIndex(key=obj.guid,timeout=1):
                        raise RuntimeError("index not stored for key:%s in %s:%s"(key,self.namespace, self.categoryname))
            else:
                if key==None:
                    if value.has_key("guid"):
                        key=value["guid"]
                    else:
                        raise RuntimeError("could not find guid attr on obj for %s:%s"(self.namespace, self.categoryname))                
                else:
                    if not value.has_key("guid"):
                        value["guid"]=key
                self.db.set(self.dbprefix, key=key, value=value2)                
                self.index(value)
                if waitIndex:
                    time.sleep(0.2)
                    if not self.existsIndex(key=obj.guid,timeout=1):
                        raise RuntimeError("index not stored for key:%s in %s:%s"(key,self.namespace, self.categoryname))               
        else:
            raise RuntimeError("val should be dict or osisobj")
        new=True
        changed=True            
        return (key,new,changed)

    def get(self, key):
        """
        get dict value
        """
        q='{"query":{"bool":{"must":[{"text":{"json.guid":"$guid"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"facets":{}}'
        q=q.replace("$guid",key)
        q=json.loads(q)
        res=self.find(q)
        if res["total"]==0:
            raise RuntimeError("cannot find %s on %s:%s"%(key,self.namespace,self.categoryname))
        else:
            return  res["result"][0]["_source"]

    def exists(self, key):
        """
        get dict value
        """
        return self.existsIndex(key,timeout=0)

    def delete(self, key):
        self.removeFromIndex(key)
        
    def list(self, prefix="", withcontent=False):
        """
        return all object id's stored in DB
        """
        raise RuntimeError("not implemented, use find")


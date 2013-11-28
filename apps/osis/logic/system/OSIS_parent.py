from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
import uuid

ujson = j.db.serializers.getSerializerType('j')

class mainclass(OSISStore):
    """
    """

    def set(self,key,value):
        obj=self.getObject(value)        
        new,changed,obj=self.setObjIds(obj)
        if changed:
            print "OBJECT CHANGED WRITE"
            # print obj
            self.db.set(self.dbprefix,key=obj.guid,value=ujson.dumps(obj.__dict__))
            self.index(obj)
        return [obj.guid,new,changed]

    def setObjIds(self,obj):
        """
        for zobject get unique id & set it in object
        return (new,changed,obj) #new & changed=boolean
        """
        ckey=obj.getContentKey()
        print "ckey:%s"%ckey
        ukey=obj.getUniqueKey()
        print "ukey:%s"%ukey
        if ukey==None or str(ukey)=="":
            raise RuntimeError("ukey cannot be empty, the obj send needs to return an nonempty obj.getUniqueKey()")
        changed=False
        new=False
        
        if self.db.exists(self.dbprefix_incr, ukey):
            print "ukey exists"
            new=False
            id,guid,ckey2=ujson.loads(self.db.get(self.dbprefix_incr, ukey))
            guid=str(guid)
            ckey=str(ckey)
            ckey2=str(ckey2)
            print "ckey in db: %s"%ckey2
            # if obj.id<>id:
            #     msg="coreobj id not in line with id in contentkey db."
            #     j.errorconditionhandler.raiseOperationalWarning(msgpub=msg,message="",category="osis.corruption")
            #     changed=True
            #     obj.id=id
            # if obj.guid<>guid:
            #     msg="coreobj guid not in line with id in contentkey db."
            #     o.errorconditionhandler.raiseOperationalWarning(msgpub=msg,message="",category="osis.corruption")
            #     changed=True
            obj.guid=guid
            obj.id=id
            if ckey2<>ckey:
                changed=True
            return (new,changed,obj)
        else:
            print "ukey not in db"
            new=True
            changed=True    
            id=self.db.increment(self.dbprefix_incr)
            print "newid:%s"%id
            obj.id=id
            obj.getSetGuid()
            ckey=obj.getContentKey()
            obj._ckey=ckey
            print "ckey for new object:%s"%ckey
            json=ujson.dumps([obj.id,obj.guid,ckey])
            self.db.set(self.dbprefix_incr, ukey, json)
            return (new,changed,obj)

        # else:
        #     obj2=ujson.loads(self.db.get(self.dbprefix, obj.guid))
        #     if obj2._ckey<>ckey:
        #         changed=True

        # if changed:
        #     obj.getSetGuid()
        #     ckey=obj.getContentKey()
        #     obj._ckey=ckey

        # return (new,changed,obj)

    def list(self,prefix="",withcontent=False):
        """
        return all object id's stored in DB
        """
        db=self.db

        if withcontent==False:
            return db.list(self.dbprefix,prefix)

        from pylabs.Shell import ipshell
        print "DEBUG NOW list with content osis (not implemented yet)" #@todo not urgent
        ipshell()

        if self.db.exists("modellist",self.modelname):
            r=self.db.get("modellist",self.modelname)
            return r

        result=[]
        for item in db.list(cat,""):
            o=self.get(guid=item)
            row=[]
            for prop in self.listProps:
                r=o.__dict__["_P_%s"%prop]
                if j.basetype.list.check(r):
                    r=",".join(r)
                if j.basetype.dictionary.check(r):
                    for key in r.keys():
                        r+="%s:%s,"%(key,r[key])
                    r.rstrip(",")
                row.append(r)
            result.append(row)
        self.db.set("modellist",self.modelname,result)
        return result

    def rebuildindex(self):
        #@todo push to worker, this will be too slow (best to create sort of mapreduce alike technique)
        self.destroyindex()
        ids=self.list()
        for id in ids:
            obj=self.unserialize(self.get(id))
            self.index(obj)



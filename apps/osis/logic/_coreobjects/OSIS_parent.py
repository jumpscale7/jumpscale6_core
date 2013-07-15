from OpenWizzy import o
from OpenWizzy.grid.osis.OSISStore import OSISStore
import uuid
class mainclass(OSISStore):
    """
    """

    def set(self,key,value):
        obj=self.getObject(value)
        new,changed,obj=self.setObjIds(obj)
        self.db.set(self.dbprefix,key=obj.guid,value=self.serialize(obj.__dict__))
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
        changed=False
        new=False
        id=0
        if ukey:
            if self.db.exists(self.dbprefix_incr, ukey):
                print "ukey exists"
                id,guid,ckey2=o.db.serializers.ujson.loads(self.db.get(self.dbprefix_incr, ukey))
                print "ckey in db: %s"%ckey2
                if obj.id<>id:    
                    msg="coreobj id not in line with id in contentkey db."
                    o.errorconditationhandler.raiseOperationalWarning(msgpub=msg,message="",category="osis.corruption")
                    changed=True
                    obj.id=id
                elif obj.guid<>guid:
                    msg="coreobj guid not in line with id in contentkey db."
                    o.errorconditationhandler.raiseOperationalWarning(msgpub=msg,message="",category="osis.corruption")
                    changed=True
                    obj.guid=guid
                elif ckey2<>ckey:
                    changed=True
                else:
                    return (False,False,obj)
            else:
                print "ukey not in db"
                new=True

            if new:
                #need to rewrite
                id=self.db.increment(self.dbprefix_incr)
                print "newid:%s"%id

            obj.id=id
            obj.getSetGuid()
            ckey=obj.getContentKey()
            obj._ckey=ckey
            print "ckey at end:%s"%ckey
            json=o.db.serializers.ujson.dumps([obj.id,obj.guid,obj.getContentKey()])
            self.db.set(self.dbprefix_incr, ukey, json)

        else:
            obj2=o.db.serializers.ujson.loads(self.db.get(self.dbprefix, obj.guid))
            if obj2._ckey<>ckey:
                changed=True

        if changed:
            obj.getSetGuid()
            ckey=obj.getContentKey()
            obj._ckey=ckey

        return (new,changed,obj)

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
                if o.basetype.list.check(r):
                    r=",".join(r)
                if o.basetype.dictionary.check(r):
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


    # def serialize(self,obj):
    #     return o.db.serializers.ujson.dumps(obj)

    # def unserialize(self,obj):
    #     return o.db.serializers.ujson.loads(obj)

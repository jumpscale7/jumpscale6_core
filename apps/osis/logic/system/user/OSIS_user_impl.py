from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace
import ujson

class mainclass(parentclass):
    """
    """

    def init(self, path, namespace,categoryname):
        """
        gets executed when category in osis gets loaded by osiscmds.py (.init method)
        """
        self.initall(path, namespace,categoryname,db=True)
        self.olddb=self.db
        
        if j.application.config.exists("rediskvs_master_addr"):
            masterdb=j.db.keyvaluestore.getRedisStore(namespace='', host=j.application.config.get("rediskvs_master_addr"), port=7772, password=j.application.config.get("rediskvs_secret"))
            self.db=j.db.keyvaluestore.getRedisStore(namespace='', host='localhost', port=7771, password='', masterdb=masterdb)
            self.db.osis[self.dbprefix]=self
        # self.db.deleteChangeLog() #for debug purposes
        
    def set(self,key,value,waitIndex=False):
        obj=self.getObject(value)        
        obj.getSetGuid()

        changed=True
        if self.exists(obj.guid):
            objexist=self.getObject(self.get(obj.guid))
            if obj.getContentKey()==objexist.getContentKey():
                changed=False
                

        if changed:
            print "OBJECT CHANGED WRITE"
            val=j.core.osis.encrypt(obj)
            self.db.set(self.dbprefix,key=obj.guid,value=val)
            self.index(obj.getDictForIndex())

            g=j.core.osis.cmds._getOsisInstanceForCat("system","group")
            for group in obj.groups:
                grkey="%s_%s"%(obj.gid,group)
                if g.exists(grkey)==False:
                    #group does not exist yet, create
                    grnew=g.getObject()
                    grnew.id=group
                    grnew.gid=obj.gid
                    grnew.domain=obj.domain
                    grnew.users=[obj.id]
                    grguid,a,b=g.set(grnew.guid,grnew.__dict__)
                else:
                    gr=g.get(grkey)
                    if obj.id not in gr['users']:
                         gr['users'].append(obj.id)
                         g.set(gr['guid'],gr)
        
        return [obj.guid,changed,changed]

    def get(self, key):
        """
        @return as json encoded
        """
        val=self.db.get(self.dbprefix, key)
        val=j.core.osis.decrypt(val,json=True)
        return val

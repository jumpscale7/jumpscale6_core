from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace
import ujson

class mainclass(parentclass):
    """
    """
    def __init__(self):
        pass
        
    def set(self,key,value):
        obj=self.getObject(value)        
        obj.getSetGuid()

        changed=True
        if self.exists(obj.guid):
            objexist=self.getObject(ujson.loads(self.get(obj.guid)))
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
                    gr=ujson.loads(g.get(grkey))
                    if obj.id not in  gr["users"]:
                         gr["users"].append(obj.id)
                         g.set(gr["guid"],gr)
                
        return [obj.guid,changed,changed]

    def get(self, key):
        """
        @return as json encoded
        """
        val=self.db.get(self.dbprefix, key)
        val=j.core.osis.decrypt(val)
        return val
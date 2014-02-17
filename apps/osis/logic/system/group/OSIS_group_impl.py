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

            u=j.core.osis.cmds._getOsisInstanceForCat("system","user")
            for user in obj.users:
                userkey="%s_%s"%(obj.gid,user)
                if u.exists(userkey)==False:
                    #group does not exist yet, create
                    usernew=u.getObject()
                    usernew.id=user
                    usernew.gid=obj.gid
                    usernew.domain=obj.domain
                    usernew.groups=[obj.id]
                    userguid,a,b=u.set(usernew.guid,usernew.__dict__)
                else:
                    user=ujson.loads(u.get(userkey))
                    if obj.id not in  user["groups"]:
                         user["groups"].append(obj.id)
                         u.set(user["guid"],user)

        return [obj.guid,changed,changed]

    def get(self, key):
        """
        @return as json encoded
        """
        val=self.db.get(self.dbprefix, key)
        val=j.core.osis.decrypt(val)
        return val
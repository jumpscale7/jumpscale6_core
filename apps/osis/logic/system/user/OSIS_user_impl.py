from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace
import bson

class mainclass(parentclass):
    """
    """

    def set(self,key,value,waitIndex=False):
        if 'passwd' in value:
            passwd = j.core.osis.encrypt(value['passwd'] or '')
            value['passwd'] = bson.Binary(passwd)
        
        guid, new, changed = super(parentclass, self).set(key, value, waitIndex)

        g=j.core.osis.cmds._getOsisInstanceForCat("system","group")
        if changed:
            for group in value['groups']:
                grkey="%s_%s"%(value['gid'],group)
                if g.exists(grkey)==False:
                    #group does not exist yet, create
                    grnew=g.getObject()
                    grnew.id=group
                    grnew.gid=value['gid']
                    grnew.domain=value['domain']
                    grnew.users=[value['id']]
                    grguid,a,b=g.set(grnew.guid,grnew.__dict__)
                else:
                    gr=g.get(grkey)
                    if value['id'] not in gr['users']:
                         gr['users'].append(value['id'])
                         g.set(gr['guid'],gr)
        
        return guid, new, changed

    def get(self, key):
        """
        @return as json encoded
        """
        val = parentclass.get(self, key)
        if 'passwd' in val:
            val['passwd'] = j.core.osis.decrypt(val['passwd'])
        return val

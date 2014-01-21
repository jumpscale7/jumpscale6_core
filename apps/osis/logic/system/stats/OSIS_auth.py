from JumpScale import j
import ujson

class AUTH():

    def load(self,osis):
        for key in osis.list():
            item=osis.get(key)
            obj=ujson.loads(item)
            j.core.osis.nodeguids[str(obj["machineguid"])]=obj["id"]

    def authenticate(self,osis,method,user,passwd):
        if j.core.osis.cmds._authenticateAdmin(user=user,passwd=passwd):
            return True
        if user=="node" and method in ["set"]:
            if j.core.osis.nodeguids.has_key(passwd):
                return True
        return False

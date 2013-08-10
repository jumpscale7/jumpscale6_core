
from OpenWizzy import o

class OSISClientForCat():
    def __init__(self,client,namespaceid,catid):
        self.namespaceid=namespaceid
        self.catid=catid
        self.client=client.client

    def set(self,value,key=None,compress=False):
        """
        if key none then key will be given by server
        serialization
         S:string or raw
         J:json
         None 
        """
        if compress:
            value=o.db.serializers.lzma.dumps(value)
        value=self.client.set(namespaceid=self.namespaceid,catid=self.catid,key=key,value=value,compress=compress)
        # value=self.client.sendcmd("set",namespaceid=self.namespaceid,catid=self.catid,key=key,value=value,compress=compress)
        return value

    def get(self,namespace,category,key,compress=False):
        value=self.client.get(namespaceid=self.namespaceid,catid=self.catid,key=key,compress=compress)
        # value=self.client.sendcmd("get",namespaceid=self.namespaceid,catid=self.catid,key=key,compress=compress)
        if compress:
            value=o.db.serializers.lzma.loads(value)
        return value

    def delete(self,namespace,category,key):
        return self.client.delete(namespaceid=self.namespaceid,catid=self.catid,key=key)

    def destroy(self,namespace,category):
        return self.client.destroy(namespaceid=self.namespaceid,catid=self.catid)

    def list(self,namespace,category,prefix=""):
        return self.client.list(namespaceid=self.namespaceid,catid=self.catid,prefix=prefix)

    def search(self,namespace,category,query, start=0, size=10):
        return self.client.search(namespaceid=self.namespaceid,catid=self.catid,query=query,
            start=start, size=size)


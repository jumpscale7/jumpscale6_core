from JumpScale import j


from .BackupClient import BackupClient

class BackupFactory:
    def __init__(self):
        self.logenable=True
        self.loglevel=5
        self._cache={}

    def get(self, backupname,blobclientName="incubaid",gitlabName="incubaid"):
        name="%s_%s"%(blobclientName,gitlabName)
        if self._cache.has_key(name):
            return self._cache[name]
        self._cache[name]= BackupClient(backupname,blobclientName, gitlabName)
        return self._cache[name]

    def _log(self,msg,category="",level=5):
        if level<self.loglevel+1 and self.logenable:
            j.logger.log(msg,category="backup.%s"%category,level=level)


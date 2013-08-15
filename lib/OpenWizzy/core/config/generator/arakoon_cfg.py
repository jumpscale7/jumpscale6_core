from OpenWizzy import o
join = o.system.fs.joinPaths

class ArakoonPyApps:

    def __init__(self, appName):
        self.appName = appName
    
    def generate_cfg(self, baseport):
        config = o.clients.arakoon.getClientConfig(self.appName)
        if config.getNodes():
            return
        baseport = int(baseport)
        s = o.manage.arakoon.getCluster(self.appName)
        if not s.listNodes():
            s.setUp(1, baseport)
        config = o.clients.arakoon.getClientConfig(self.appName)
        if not config.getNodes():
            config.generateFromServerConfig()

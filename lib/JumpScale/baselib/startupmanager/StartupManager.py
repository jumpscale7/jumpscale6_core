from JumpScale import j
import os

# def checkPort(*args, **kwargs):
#     watcher = kwargs['watcher']
#     portstr = watcher.env.get('WAIT_FOR_PORT')
#     if portstr:
#         port = int(portstr)
#         return j.system.net.waitConnectionTest('localhost', port, 20)
#     else:
#         raise RuntimeError('Environment variable WAIT_FOR_PORT is not set')

class Process:
    def __init__(self):
        self.p

class StartupManager:
    def __init__(self):
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup')

    def addProcess(self, name, cmd, args="", env={}, numprocesses=1, priority=0, shell=False, workingdir=None,jpackage=None,domain=""):

        envstr=""
        for key in env.keys():
            envstr+="%s:%s,"%(key,env[key])
        envstr=envstr.rstrip(",")

        hrd="process.name=%s\n"%name
        if domain=="" and jpackage<>None:
            domain=jpackage.domain
        hrd="process.domain=%s\n"%domain
        hrd+="process.cmd=%s\n"%cmd
        hrd+="process.args=%s\n"%args
        hrd+="process.env=%s\n"%envstr
        hrd+="process.numprocesses=%s\n"%numprocesses
        hrd+="process.priority=%s\n"%priority
        hrd+="process.workingdir=%s\n"%workingdir
        if jpackage==None:
            hrd+="process.jpackage.domain=\n"
            hrd+="process.jpackage.name=\n"
            hrd+="process.jpackage.version=\n"
        else:
            hrd+="process.jpackage.domain=%s\n"%jpackage.domain
            hrd+="process.jpackage.name=%s\n"%jpackage.name
            hrd+="process.jpackage.version=%s\n"%jpackage.version

        j.system.fs.writeFile(filename=j.system.fs.joinPaths(self._configpath ,"%s__%s.hrd"%(domain,name)),contents=hrd)

        for item in j.system.fs.listFilesInDir("/etc/init.d"):
            itembase=j.system.fs.getBaseName(item)
            if itembase.lower().find(name)<>-1:
                #found process in init.d
                j.system.process.execute("/etc/init.d/%s stop"%itembase)
                j.system.fs.remove(item)

        for item in j.system.fs.listFilesInDir("/etc/init"):
            itembase=j.system.fs.getBaseName(item)
            if itembase.lower().find(name)<>-1:
                #found process in init
                j.system.process.execute("stop %s"%itembase)
                j.system.fs.remove(item)

        servercfg.write()

    def load(self):
        for path in j.system.fs.listFilesInDir(self._configpath , recursive=False):
            domain,name=j.system.fs.getBaseName(path).replace(".hrd","").split("__")



    def startJPackage(self,jpackage):
        from IPython import embed
        print "DEBUG NOW startjpackage"
        embed()
        

    def addEnv(self, name, env_vars):
        '''Adds [env] section
        name: watcher name
        env_vars: environment vars to set
        '''
        servercfg = self._getIniFile(name)
        sectionname = "env:%s" % name
        if not servercfg.checkSection(sectionname):
            servercfg.addSection(sectionname)
        for k, v in env_vars.iteritems():
            servercfg.addParam(sectionname, k, v)

        servercfg.write()

    def _getIniFile(self, name):
        inipath = j.system.fs.joinPaths(self._configpath, name + ".ini")
        return j.tools.inifile.open(inipath)

    def _getIniFilePath(self, name):
        return j.system.fs.joinPaths(self._configpath, name + ".ini")

    def removeProcess(self,name):
        servercfg = self._getIniFilePath(name)
        if j.system.fs.exists(servercfg):
            j.system.fs.remove(servercfg)
        from IPython import embed
        print "DEBUG NOW removeprocess"
        embed()
        

    def status(self, process=None):
        """
        get status of process if not process is given return status of circus
        """
        status = j.tools.circus.client.status()
        if process:
            return status['statuses'].get(process, 'notfound')
        else:
            return status['status']

    def apply(self):
        """
        make sure circus knows about it
        """
        from IPython import embed
        print "DEBUG NOW apply"
        embed()
        

    def listProcesses(self):
        from IPython import embed
        print "DEBUG NOW listProcesses"
        embed()

    def startProcess(self, name):
        j.tools.circus.client.startWatcher(name)

    def stopProcess(self, name):
        j.tools.circus.client.stopWatcher(name)

    def restartProcess(self, name):
        j.tools.circus.client.restartWatcher(name)

    def reloadProcess(self, name):
        j.tools.circus.client.reloadWatcher(name)

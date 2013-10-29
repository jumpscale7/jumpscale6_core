from JumpScale import j

class CircusManager:
    def __init__(self):
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup')

    def addProcess(self, name, cmd, args="", warmup_delay=0, numprocesses=1, priority=0, autostart=True,shell=False,workingdir=None, send_hup=False):
        servercfg = self._getIniFile(name)
        sectionname = "watcher:%s" % name
        if servercfg.checkSection(sectionname):
            servercfg.removeSection(sectionname)
        servercfg.addSection(sectionname)
        servercfg.addParam(sectionname, 'cmd', cmd)
        servercfg.addParam(sectionname, 'args', args)
        servercfg.addParam(sectionname, 'warmup_delay', warmup_delay)
        servercfg.addParam(sectionname, 'numprocesses', numprocesses)
        servercfg.addParam(sectionname, 'priority', priority)
        servercfg.addParam(sectionname, 'autostart', autostart)
        servercfg.addParam(sectionname, 'send_hup', send_hup)
        if workingdir<>None:
            servercfg.addParam(sectionname, 'workingdir', workingdir)
        servercfg.addParam(sectionname, 'shell', shell)
        #check name is no service yet and if then remove

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

        j.tools.circus.manager.apply()


    def _getIniFile(self, name):
        inipath = j.system.fs.joinPaths(self._configpath, name + ".ini")
        return j.tools.inifile.open(inipath)

    def _getIniFilePath(self, name):
        return j.system.fs.joinPaths(self._configpath, name + ".ini")

    def removeProcess(self,name):
        servercfg = self._getIniFilePath(name)
        if j.system.fs.exists(servercfg):
            j.system.fs.remove(servercfg)
        j.tools.circus.client.rm(name=name)

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
        j.tools.circus.client.reload()
        j.tools.circus.client.reloadconfig()

    def listProcesses(self):
        return j.tools.circus.client.listWatchers()

    def startProcess(self, name):
        j.tools.circus.client.startWatcher(name)

    def stopProcess(self, name):
        j.tools.circus.client.stopWatcher(name)

    def restartProcess(self, name):
        j.tools.circus.client.restartWatcher(name)

    def reloadProcess(self, name):
        j.tools.circus.client.reloadWatcher(name)
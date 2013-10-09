from JumpScale import j


class CircusManager:
    def __init__(self):
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup', 'server.ini')

    def addProcess(self, name, cmd, args="", warmup_delay=0, numprocesses=1, priority=0, autostart=False):
        servercfg = j.tools.inifile.open(self._configpath)
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

    def removeProcess(self,name):
        servercfg = j.tools.inifile.open(self._configpath)
        sectionname = "[watcher:%s]" % name
        if servercfg.checkSection(sectionname):
            servercfg.removeSection(sectionname)
        j.tools.circus.client.rm(name=name)

    def apply(self):
        """
        make sure circus knows about it
        """
        j.tools.circus.client.reload()
        j.tools.circus.client.reloadconfig()

    def listProcesses(self):
        servercfg = j.tools.inifile.open(self._configpath)
        items = [section.split(':', 1)[1] for section in servercfg.getSections() if section.startswith('watcher')]
        return items

    def startProcess(self, name):
        j.system.installtools.execute("circusctl start %s" % name)

    def stopProcess(self, name):
        j.system.installtools.execute("circusctl stop %s" % name)

    def restartProcess(self, name):
        j.system.installtools.execute("circusctl restart %s" % name)

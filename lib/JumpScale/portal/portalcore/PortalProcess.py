import gevent
import sys
from gevent.server import StreamServer

from JumpScale import j
import inspect
import time
import os
from PortalTCPChannels import ManholeSession, WorkerSession, TCPSessionLog

try:
    import fcntl
except:
    pass

#from PortalCoreWebservices import *

#from ActorLoaderPortal import ActorLoaderPortal

#from MessageRouter import MessageRouter


# class Scheduler():

#     def __init__(self):
#         self.tasks = {}

#     def check(self, epoch):
#         for key in self.tasks.keys():
#             task = self.tasks[key]
#             task.check(epoch)

#     def _queueTask(self, executionEpoch, waitTime, method, **params):
#         key = "%s_%s" % (method.func_code.co_name, str(params).replace("\n", ""))
#         self.tasksScheduled[key].append(self.epoch + waitTime)
#         self.taskQueue.append([executionEpoch, waitTime, method, params])

#     def scheduleFromNow(self, secFromNow, minimalPeriod, method, **args):
#         self.schedule(j.core.portal.runningPortal.epoch + secFromNow, minimalPeriod, 0, method, **args)

#     def scheduleNow(self, minimalPeriod, method, **args):
#         task = self.schedule(0, minimalPeriod, 0, method, **args)
#         task.check(j.core.portal.runningPortal.epoch)

#     def schedule(self, executionEpoch, minimalPeriod, recurringPeriod, method, **args):
#         print self.tasks
#         key = "%s_%s" % (method.func_code.co_name, str(args).replace("\n", ""))
#         if key not in self.tasks:
#             self.tasks[key] = Task(method, args, executionEpoch, minimalPeriod, recurringPeriod)
#             return self.tasks[key]
#         else:
#             task = self.tasks[key]
#             task.minimalPeriod = minimalPeriod
#             task.recurringPeriod = recurringPeriod
#             task.schedule(executionEpoch)
#             return task


# class Task():

#     def __init__(self, method, args, executionEpoch, minimalPeriod, recurringPeriod):
#         self.scheduled = []
#         self.method = method
#         self.args = args
#         self.lastRun = 0
#         self.key = self.getKey()
#         self.recurringPeriod = recurringPeriod
#         self.minimalPeriod = minimalPeriod
#         self.schedule(executionEpoch)

#     def schedule(self, executionEpoch):
#         self.scheduled.append(executionEpoch)

#     def check(self, epoch):
#         # check recurring
#         if self.recurringPeriod != 0 and self.lastRun + self.recurringPeriod < epoch:
#             self.execute(epoch)
#             # check with scheduled tasks we can remove
#             for x in range(0, len(self.scheduled)):
#                 epochschedule = self.scheduled[x]
#                 if epochschedule < self.lastRun + self.recurringPeriod:
#                     self.scheduled.pop(x)
#                     x = x - 1
#                 else:
#                     return
#             return

#         for x in range(0, len(self.scheduled)):
#             epochschedule = self.scheduled[x]
#             if epoch > epochschedule:
#                 if self.lastRun + self.minimalPeriod < epoch:
#                     self.execute(epoch)
#                     self.scheduled = [item for item in self.scheduled if not (item < self.lastRun + self.minimalPeriod)]
#                     return
#             else:
#                 break

#     def execute(self, epoch):
#         self.method(**self.args)
#         self.scheduled.pop(0)
#         self.lastRun = epoch

#     def getKey(self):
#         self.key = "%s_%s" % (self.method.func_code.co_name, str(self.args).replace("\n", ""))
#         return self.key


class PortalProcess():

    """
    """

    def __init__(self, processNr=1, mainLoop=None, inprocess=False, cfgdir="", startdir=""):

        self.started = False
        # self.logs=[]
        # self.errors=[]
        self.epoch = time.time()
        self.lock = {}

        j.core.portal.runningPortal = self

        self.actorsloader = j.core.portalloader.getActorsLoader()

        self.taskletengines = {}

        self.actors = {}  # key is the applicationName_actorname (lowercase)

        # j.errorconditionhandler.setExceptHook() #@does not do much?

        # Trigger the key value store extension so the enum is loaded
        self.cfgdir = cfgdir

        if self.cfgdir == "":
            self.cfgdir = "cfg"

        # check if the dir we got started from is a link, if so will create a new dir and copy the config files to there
        if j.system.fs.isLink(startdir, True):
            # we are link do not use this config info
            name = j.system.fs.getDirName(startdir + "/", True) + "_localconfig"
            newpath = j.system.fs.joinPaths(j.system.fs.getParent(startdir + "/"), name)
            if not j.system.fs.exists(newpath):
                j.system.fs.createDir(newpath)
                pathcfgold = j.system.fs.joinPaths(startdir, "cfg")
                j.system.fs.copyDirTree(pathcfgold, newpath)
            self.cfgdir = newpath

        ini = j.tools.inifile.open(self.cfgdir + "/appserver.cfg")

        if ini.checkParam("main", "appdir"):
            self.appdir = self._replaceVar(ini.getValue("main", "appdir"))
        else:
            self.appdir = j.system.fs.getcwd()

        # self.codepath=ini.getValue("main","codepath")
        # if self.codepath.strip()=="":
            #self.codepath=j.system.fs.joinPaths( j.dirs.varDir,"actorscode")
        # j.system.fs.createDir(self.codepath)

        # self.specpath=ini.getValue("main","specpath")
        # if self.specpath.strip()=="":
            # self.specpath="specs"
        # if not j.system.fs.exists(self.specpath):
            #raise RuntimeError("spec path does have to exist: %s" % self.specpath)

        dbtype = ini.getValue("main", "dbtype").lower().strip()
        if dbtype == "fs":
            self.dbtype = j.enumerators.KeyValueStoreType.FILE_SYSTEM
        elif dbtype == "mem":
            self.dbtype = j.enumerators.KeyValueStoreType.MEMORY
        elif dbtype == "redis":
            self.dbtype = j.enumerators.KeyValueStoreType.REDIS
        elif dbtype == "arakoon":
            self.dbtype = j.enumerators.KeyValueStoreType.ARAKOON
        else:
            raise RuntimeError("could not find appropriate core db, supported are: fs,mem,redis,arakoon")

        # self.systemdb=j.db.keyvaluestore.getFileSystemStore("appserversystem",baseDir=self._replaceVar(ini.getValue("systemdb","dbdpath")))

        self.processNr = processNr

        skey = "process_%s" % self.processNr
        if not ini.checkSection(skey):
            raise RuntimeError("Could not find process_%s section in config file for appserver" % processNr)

        self.ipaddr = ini.getValue("main", "ipaddr")

        if ini.checkParam('main', 'dns'):
            self.dns = ini.getValue('main', 'dns')
        else:
            self.dns = self.ipaddr.split(',')[0]

        self.secret = ini.getValue(skey, "secret").strip()

        self.wsport = int(ini.getValue(skey, "webserverport"))

        self.filesroot = self._replaceVar(ini.getValue("main", "filesroot"))

        self.filesroot = self._replaceVar(ini.getValue("main", "filesroot"))

        if self.wsport > 0 and inprocess == False:
            self.webserver = j.web.geventws.get(self.wsport, self.secret, wwwroot=ini.getValue("main", "wwwroot"),
                                                filesroot=self.filesroot, cfgdir=cfgdir)
        else:
            self.webserver = None

        self._greenLetsPath = j.system.fs.joinPaths(j.dirs.varDir, "portal_greenlets", self.wsport)
        j.system.fs.createDir(self._greenLetsPath)
        sys.path.append(self._greenLetsPath)

        self.tcpserver = None
        self.tcpservercmds = {}
        tcpserverport = int(ini.getValue(skey, "tcpserverport", default=0))
        if tcpserverport > 0 and inprocess == False:
            self.tcpserver = StreamServer(('0.0.0.0', tcpserverport), self.socketaccept)

        manholeport = int(ini.getValue(skey, "manholeport", default=0))
        self.manholeserver = None
        if manholeport > 0 and inprocess == False:
            self.manholeserver = StreamServer(('0.0.0.0', manholeport), self.socketaccept_manhole)

        if inprocess == False and (manholeport > 0 or tcpserverport > 0):
            self.sessions = {}
            self.nrsessions = 0

        # self.messagerouter=MessageRouter()

        # self.logserver=None
        self.logserver_enable = False
        # if logserver==True:
            #self.logserver=StreamServer(('0.0.0.0', 6002), self.socketaccept_log)
            # self.logserver_enable=True
        # elif logserver<>None:
            # @todo configure the logging framework
            # pass

        self.ecserver_enable = False
        # self.ecserver=None #errorconditionserver
        # if ecserver==True:
            #self.ecserver=StreamServer(('0.0.0.0', 6003), self.socketaccept_ec)
            # self.ecserver_enable=True
        # elif ecserver<>None:
            # @todo configure the errorcondition framework
            # pass

        self.signalserver_enable = False
        # self.signalserver=None #signal handling
        # if signalserver==True:
            #self.signalserver=StreamServer(('0.0.0.0', 6004), self.socketaccept_signal)
            # self.signalserver_enable=True
        # elif signalserver<>None:
            # @todo configure the signal framework
            # pass

        self.mainLoop = mainLoop
        j.core.portal.runningPortal = self

        self.ismaster = int(ini.getValue(skey, "ismaster")) == 1

        self.cfg = ini

        self.redisServersLocal = {}
        if ini.checkSection('redis') and int(ini.getValue("redis", "local")) == 1:
            rediscfg = ini.getValue("redis", "actors")
            self.rediscfg = rediscfg.split(",")
            self.rediscfg = [item.strip() for item in self.rediscfg]

            # check redis installed
            if not j.system.platformtype.isWindows():
                j.system.platform.ubuntu.checkInstall(["python-redis", "redis-server"], "redis-server")  #@todo P1 put in jpackage
        else:
            self.rediscfg = None

        # toload=[]
        self.bootstrap()

        if self.ismaster:
            self.actorsloader.getActor("system", "master")
            self.master = j.apps.system.master.extensions.master
            # self.master._init()
            # self.master.gridmapPrevious=None
            # self.master.gridMapSave()
            # self.master.gridMapRegisterPortal(self.ismaster,self.ipaddr,self.wsport,self.secret)

            # look for nginx & start
            self.startNginxServer()
            # self.scheduler = Scheduler()

        else:
            self.master = None
            #from JumpScale.core.Shell import ipshellDebug,ipshell
            # print "DEBUG NOW not implemented yet in appserver6process, need to connect to other master & master client"
            # ipshell()

        self.loadFromConfig()

    def reset(self):
        self.bootstrap()
        self.loadFromConfig()

    def bootstrap(self):
        self.actorsloader.reset()
        self.actorsloader._generateLoadActor("system", "contentmanager", actorpath="system/system__contentmanager/")
        self.actorsloader._generateLoadActor("system", "master", actorpath="system/system__master/")
        self.actorsloader._generateLoadActor("system", "usermanager", actorpath="system/system__usermanager/")
        self.actorsloader.scan("system")
        self.actorsloader.getActor("system", "usermanager")
        self.actorsloader.getActor("system", "errorconditionhandler")

        self.actorsloader._getSystemLoaderForUsersGroups()

    def loadFromConfig(self, reset=False):
        if reset:
            j.core.codegenerator.resetMemNonSystem()
            j.core.specparser.resetMemNonSystem()
            self.webserver.contentdirs = {}

        loader = self.actorsloader
        self.webserver.loadFromConfig4loader(loader, reset)

    def _replaceVar(self, txt):
        txt = txt.replace("$qbase", j.dirs.baseDir).replace("\\", "/")
        txt = txt.replace("$appdir", j.system.fs.getcwd()).replace("\\", "/")
        txt = txt.replace("$vardir", j.dirs.varDir).replace("\\", "/")
        txt = txt.replace("$htmllibdir", j.html.getHtmllibDir()).replace("\\", "/")
        txt = txt.replace("\\", "/")
        return txt

    def startNginxServer(self):

        ini = j.tools.inifile.open("cfg/appserver.cfg")
        local = int(ini.getValue("nginx", "local")) == 1

        configtemplate = j.system.fs.fileGetContents(j.system.fs.joinPaths(j.core.portal.getConfigTemplatesPath(), "nginx", "appserver_template.conf"))
        configtemplate = self._replaceVar(configtemplate)

        if local:
            varnginx = j.system.fs.joinPaths(j.dirs.varDir, 'nginx')
            j.system.fs.createDir(varnginx)
            if j.system.platformtype.isWindows():

                apppath = self._replaceVar(ini.getValue("nginx", "apppath")).replace("\\", "/")

                cfgpath = j.system.fs.joinPaths(apppath, "conf", "sites-enabled", "appserver.conf")
                j.system.fs.writeFile(cfgpath, configtemplate)

                apppath2 = j.system.fs.joinPaths(apppath, "start.bat")
                cmd = "%s %s" % (apppath2, apppath)
                cmd = cmd.replace("\\", "/").replace("//", "/")

                extpath = inspect.getfile(self.__init__)
                extpath = j.system.fs.getDirName(extpath)
                maincfg = j.system.fs.joinPaths(extpath, "configtemplates", "nginx", "nginx.conf")
                configtemplate2 = j.system.fs.fileGetContents(maincfg)
                configtemplate2 = self._replaceVar(configtemplate2)
                j.system.fs.writeFile("%s/conf/nginx.conf" % apppath, configtemplate2)

                pid = j.system.windows.getPidOfProcess("nginx.exe")
                if pid != None:
                    j.system.process.kill(pid)

                pid = j.system.windows.getPidOfProcess("php-cgi.exe")
                if pid != None:
                    j.system.process.kill(pid)

                j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.varDir, "nginx"))

                print "start nginx, cmd was %s" % (cmd)
                j.system.process.executeAsync(cmd, outputToStdout=False)

            else:
                j.system.platform.ubuntu.check()

                j.system.fs.remove("/etc/nginx/sites-enabled/default")

                cfgpath = j.system.fs.joinPaths("/etc/nginx/sites-enabled", "appserver.conf")
                j.system.fs.writeFile(cfgpath, configtemplate)

                if not j.system.fs.exists("/etc/nginx/nginx.conf.backup"):
                    j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.varDir, "nginx"))
                    maincfg = j.system.fs.joinPaths(j.core.portal.getConfigTemplatesPath(), "nginx", "nginx.conf")
                    configtemplate2 = j.system.fs.fileGetContents(maincfg)
                    configtemplate2 = self._replaceVar(configtemplate2)
                    j.system.fs.copyFile("/etc/nginx/nginx.conf", "/etc/nginx/nginx.conf.backup")
                    j.system.fs.writeFile("/etc/nginx/nginx.conf", configtemplate2)
                    j.system.process.execute("/etc/init.d/nginx restart")

                j.system.process.execute("/etc/init.d/nginx reload")


        else:
            pass
            #raise RuntimeError("only supported in nginx mode")

    def startConnectRedisServer(self, appname, actorname, instance=0):
        ini = self.cfg
        allinone = ini.getIntValue("redis", "allinone") == 1

        if not int(ini.getValue("redis", "local")) == 1:
            return

        launch = False
        if actorname.find("_model_") != -1:
            actorname = actorname.split("_model_")[0]
        else:
            actorname = actorname

        port = None
        key = "%s__%s" % (appname, actorname)
        print key
        if "*" in self.rediscfg:
            launch = True
        elif appname in self.rediscfg:
            launch = True
        elif key in self.rediscfg:
            launch = True

        ip = self.ipaddr
        secret = self.secret
        rediscfg = False
        if allinone == False:
            rediscfg = self.master.gridMapGetRedisClusterFromAppActorName(appname, actorname)
            if rediscfg != False:
                ip, port = rediscfg.hosts[0].split(":")
                secret = rediscfg.secret
                launch = False
                if j.clients.redis.ping(ip, port, secret) == False:
                    print "The redis instance %s %s was not started, try to start now" % (ip, port)
                    launch = True

        if allinone and len(self.redisServersLocal.keys()) > 0:
            # means there is already 1 local redisserver
            p = self.redisServersLocal.keys()[0]
            return ip, self.redisServersLocal[p], 0, secret

        sysdb = self.systemdb

        lastport = port

        if launch:
            redisportrangeFrom = int(ini.getValue("redis", "portrangeFrom"))
            redisportrangeTo = int(ini.getValue("redis", "portrangeTo"))

            if j.system.platformtype.isWindows():
                redisapppath = self._replaceVar(ini.getValue("redis", "apppath")).replace("\\", "/")
                redisdbdpath = self._replaceVar(ini.getValue("redis", "dbdpath")).replace("\\", "/")
            else:
                redisapppath = ""
                redisdbdpath = j.system.fs.joinPaths(j.dirs.varDir, "redis")

            j.system.fs.createDir(redisdbdpath)

            if not sysdb.exists("rediscfg", key):
                lastport = redisportrangeFrom + sysdb.increment("rediscfg_lastport")
                if lastport > redisportrangeTo:
                    raise RuntimeError("not enough ports for redis, cannot start more, max amount of actors reached")
                sysdb.set("rediscfg", key, lastport)
            else:
                lastport = sysdb.get("rediscfg", key)

            templpath = j.system.fs.joinPaths(j.core.portal.getConfigTemplatesPath(), "redis", "redis_template.conf")
            configtemplate = j.system.fs.fileGetContents(templpath)
            configtemplate = configtemplate.replace("$port", str(lastport))
            configtemplate = configtemplate.replace("$key", key)
            configtemplate = configtemplate.replace("$dir", redisdbdpath)

            cfgpath = j.system.fs.joinPaths(redisdbdpath, "redis_%s_%s.conf" % (appname, actorname))
            j.system.fs.writeFile(cfgpath, configtemplate)

            if j.system.platformtype.isWindows():
                apppath2 = j.system.fs.joinPaths(redisapppath, "start.bat")
                cmd = "%s %s %s" % (apppath2, redisapppath, cfgpath)
                print "start redis for actor %s %s, cmd was %s" % (appname, actorname, cmd)
                j.system.process.executeAsync(cmd, outputToStdout=False)
            else:
                j.system.process.executeAsync("redis-server", [cfgpath], False, False, False, False, False)

            self.redisServersLocal[key] = lastport

        if "*" in self.rediscfg:
            self.redisServersLocal["*"] = lastport
        elif appname in self.rediscfg:
            self.redisServersLocal[appname] = lastport
        port = lastport

        # need to register in gridmap

        if rediscfg == False:
            rediscfg = self.gridmap.new_rediscluster()
            rediscfg.hosts.append("%s:%s" % (ip, port))
            rediscfg.secret = self.secret
        else:
            rediscfg.secret = self.secret
            rediscfg.hosts = []
            rediscfg.hosts.append("%s:%s" % (ip, port))

        self.gridmap.actor2redis[key] = rediscfg.id

        ai = self.gridmap.new_actorinstance("%s_%s_%s" % (appname, actorname, instance))
        ai.actorname = actorname
        ai.appname = appname
        ai.instance = instance
        ai.ismodel = False
        ai.redisclusterid = rediscfg.id
        self.master.gridMapSave()

        return ip, port, 0, secret

    def activateActor(self, appname, actor):
        if not "%s_%s" % (appname, actor) in self.actors.keys():
            # need to activate
            result = self.actorsloader.getActor(appname, actor)
            if result == None:
                # there was no actor
                return False

    def addTCPServerCmd(self, cmdName, function):
        self.tcpservercmds[cmdName] = function

    def setTcpServer(self, socketAcceptFunction):
        self.tcpserver = StreamServer(('0.0.0.0', 6000), socketAcceptFunction)

    def _addsession(self, session):
        self.sessions[self.nrsessions] = session
        session.sessionnr = self.nrsessions
        self.nrsessions += 1
        session.ready()
        return self.nrsessions - 1

    # this handler will be run for each incoming connection in a dedicated greenlet
    def socketaccept_manhole(self, socket, address):
        ip, port = address
        socket.sendall('Manhole For Portal Server \n\n')
        session = ManholeSession(ip, port, socket)
        self._addsession(session)
        session.run()

    def socketaccept(self, socket, address):
        ip, port = address
        session = WorkerSession(ip, port, socket)
        self._addsession(session)

    def socketaccept_log(self, socket, address):
        ip, port = address
        session = TCPSessionLog(ip, port, socket)
        self._addsession(session)

    # def socketaccept_ec(self,socket, address):
    #    ip,port=address
    #    session=TCPSessionEC(ip,port,socket)
    #    self._addsession(session)

    # def socketaccept_signal(self,socket, address):
    #    ip,port=address
    #    session=TCPSessionSignal(ip,port,socket)
    #    self._addsession(session)

    def _timer(self):
        """
        will remember time every 1/10 sec
        """
        while True:
            # self.epochbin=struct.pack("I",time.time())
            self.epoch = time.time()
            gevent.sleep(0.1)

    # def _taskSchedulerTimer(self):
    #     """
    #     every 4 seconds check maintenance queue
    #     """
    #     while True:
    #         gevent.sleep(5)
    #         self.scheduler.check(self.epoch)

    def addQGreenlet(self, appName, greenlet):
        """
        """
        if self.webserver == None:
            return
        qGreenletObject = greenlet()
        if qGreenletObject.method == "":
            raise RuntimeError("greenlet class needs to have a method")
        if qGreenletObject.actor == "":
            raise RuntimeError("greenlet class needs to have a actor")

        qGreenletObject.server = self
        self.webserver.addRoute(function=qGreenletObject.wscall,
                                appname=appName,
                                actor=qGreenletObject.actor,
                                method=qGreenletObject.method,
                                paramvalidation=qGreenletObject.paramvalidation,
                                paramdescription=qGreenletObject.paramdescription,
                                paramoptional=qGreenletObject.paramoptional,
                                description=qGreenletObject.description, auth=qGreenletObject.auth)

    def start(self, key=None, reset=False):

        # this is the trigger to start
        print "STARTING applicationserver on port %s" % self.wsport

        TIMER = gevent.greenlet.Greenlet(self._timer)
        TIMER.start()

        if self.mainLoop != None:
            MAINLOOP = gevent.greenlet.Greenlet(self.mainLoop)
            MAINLOOP.start()

        self.started = True

        if self.tcpserver != None:
            self.tcpserver.start()
        if self.manholeserver != None:
            self.manholeserver.start()
        if self.logserver_enable == True:
            self.logserver.start()
        if self.ecserver_enable == True:
            self.ecserver.start()
        if self.signalserver_enable == True:
            self.signalserver.start()

        if not self.ismaster:

            from JumpScale.core.Shell import ipshell
            print "DEBUG NOW start is not master"
            ipshell()
            self.masterClient = j.core.portal.getPortalClient("127.0.0.1", 9000, "1234")
            # self.masterSystemActor=client.getActor("system","manager",instance=0)
            # contact master & populate gridmap there
            # self.masterClient
            # j.core.portal.gridmaplocal.data

        else:
            # is master
            ipaddr = self.ipaddr
            if ipaddr == "localhost":
                ipaddr = "127.0.0.1"
            #@todo implement registration
            # for app,actorname,instance,ipaddr,port,secret in j.core.portal.gridmaplocal.datalist:
                # j.core.portal.gridmap.set(app,actorname,instance,ipaddr,port,secret)

        # self.redirectErrors()

        if self.webserver != None:
            self.webserver.start(reset=reset)

    def processErrorConditionObject(self, eco):
        print eco
        #@todo need to forward to logger

    def redirectErrors(self):
        j.errorconditionhandler.processErrorConditionObject = self.processErrorConditionObject  # @todo kds redirect

    def restartInProcess(self, app):
        args = sys.argv[:]
        args.insert(0, sys.executable)
        apppath = j.system.fs.joinPaths(j.dirs.appDir, app)
        max_fd = 1024
        for fd in range(3, max_fd):
            try:
                flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            except IOError:
                continue
            fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
        os.chdir(apppath)
        os.execv(sys.executable, args)

    # def getRedisClient(self,appname,actorname):

        # if ini.checkSection("redis"):
            # redisip=ini.getValue("redis","ipaddr")
            # redisport=ini.getValue("redis","port")
            #redisclient=redis.StrictRedis(host=redisip, port=int(redisport), db=0)
        # else:
            # redisclient=None
        # return redisclient

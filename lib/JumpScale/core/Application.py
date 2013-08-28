from JumpScale import j
import os
import atexit
import struct
from JumpScale.core.enumerators import AppStatusType
from collections import namedtuple

WhoAmI = namedtuple('WhoAmI', 'gid bid pid nid')

#@todo Need much more protection: cannot change much of the state (e.g. dirs) once the app is running!
#@todo Need to think through - when do we update the qpidfile (e.g. only when app is started ?)
#@todo can we make this a singleton? Then need to change __init__ to avoid clearing the content
#@todo need to implement QApplication.getVar()


class Application:

    def __init__(self):
        self.state = AppStatusType.UNKNOWN
        # self.state = None
        self.appname = 'starting'
        self.agentid = "starting"
        self._calledexit = False
        self.skipTraceback = False

        self._whoAmIBytestr = None
        self._whoAmI = None

        self.config = None

    @property
    @j.logger.nologger
    def whoAmI(self):
        if not self._whoAmI:
            self.initWhoAmI()
        return self._whoAmI

    @property
    @j.logger.nologger
    def whoAmIBytestr(self):
        if not self._whoAmIBytestr:
            self.initWhoAmI()
        return self._whoAmIBytestr

    def initWhoAmI(self,grid=False):
        """
        when in grid:
            is gid,bid,nid,pid
        """

        self.loadConfig()
        if self.config != None:
            nodeid = self.config.getInt("node.id")
            gridid = self.config.getInt("grid.id")
            j.logger.log("gridid:%s,nodeid:%s"%(gridid, nodeid), level=3, category="application.startup")
        else:
            gridid = 0
            nodeid = 0

        if grid:
            self._whoAmI = WhoAmI(gid=j.core.grid.processobject.gid,bid=j.core.grid.processobject.bid,\
                nid=j.core.grid.processobject.nid,pid=j.core.grid.processobject.id)
            self._whoAmIBytestr = struct.pack("<hhhh", self._whoAmI.pid,self._whoAmI.nid, self._whoAmI.bid, self._whoAmI.gid)
        else:
            self._whoAmI = WhoAmI(gid=gridid, nid=nodeid, pid=os.getpid(), bid=0)
            self._whoAmIBytestr = struct.pack("<hhh", self._whoAmI.pid, self._whoAmI.nid, self._whoAmI.gid)

    def getWhoAmiStr(self):
        return "_".join([str(item) for item in self.whoAmI])

    def loadConfig(self):
        path = j.system.fs.joinPaths(j.dirs.cfgDir, "grid", "node.hrd")
        if j.system.fs.exists(path=path):
            self.config = j.core.hrd.getHRDTree(path=j.system.fs.joinPaths(j.dirs.cfgDir, "grid"))


    def start(self,name=None,basedir="/opt/jumpscale",appdir="."):
        '''Start the application

        You can only stop the application with return code 0 by calling
        j.Application.stop(). Don't call sys.exit yourself, don't try to run
        to end-of-script, I will find you anyway!
        '''
        if name:
            self.appname = name
        if self.state == AppStatusType.RUNNING:
            raise RuntimeError("Application %s already started" % self.appname)

        # Register exit handler for sys.exit and for script termination
        atexit.register(self._exithandler)


        j.dirs.appDir=appdir
        j.dirs.baseDir=basedir

        j.dirs.init(reinit=True)

        # Set state
        self.state = AppStatusType.RUNNING

        self.initWhoAmI()

        j.logger.log("Application %s started" % self.appname, level=8, category="jumpscale.app")

    def stop(self, exitcode=0):

        '''Stop the application cleanly using a given exitcode

        @param exitcode: Exit code to use
        @type exitcode: number
        '''
        import sys

        #@todo should we check the status (e.g. if application wasnt started, we shouldnt call this method)
        if self.state == AppStatusType.UNKNOWN:
            # Consider this a normal exit
            self.state = AppStatusType.HALTED
            j.logger.close()
            sys.exit(exitcode)

        # Since we call os._exit, the exithandler of IPython is not called.
        # We need it to save command history, and to clean up temp files used by
        # IPython itself.
        j.logger.log("Stopping Application %s" % self.appname, 8)
        try:
            __IPYTHON__.atexit_operations()
        except:
            pass

        # Write exitcode
        if self.writeExitcodeOnExit:
            exitcodefilename = j.system.fs.joinPaths(j.dirs.tmpDir, 'qapplication.%d.exitcode'%os.getpid())
            j.logger.log("Writing exitcode to %s" % exitcodefilename, 5)
            j.system.fs.writeFile(exitcodefilename, str(exitcode))

        # Closing the LogTargets
        j.logger.close()

        # was probably done like this so we dont end up in the _exithandler
        # os._exit(exitcode) Exit to the system with status n, without calling cleanup handlers, flushing stdio buffers, etc. Availability: Unix, Windows.

        self._calledexit = True  # exit will raise an exception, this will bring us to _exithandler
                              # to remember that this is correct behaviour we set this flag
        sys.exit(exitcode)

    def _exithandler(self):
        # Abnormal exit
        # You can only come here if an application has been started, and if
        # an abnormal exit happened, i.e. somebody called sys.exit or the end of script was reached
        # Both are wrong! One should call j.application.stop(<exitcode>)
        #@todo can we get the line of code which called sys.exit here?
        
        #j.logger.log("UNCLEAN EXIT OF APPLICATION, SHOULD HAVE USED j.application.stop()", 4)
        j.logger.close()
        if not self._calledexit:
            self.stop(1)

    def getCPUUsage(self):
        """
        try to get cpu usage, if it doesn't work will return 0
        By default 0 for windows
        """
        try:
            pid = os.getpid()
            if j.system.platformtype.isWindows():
                return 0
            if j.system.platformtype.isLinux():
                command = "ps -o pcpu %d | grep -E --regex=\"[0.9]\""%pid
                j.logger.log("getCPUusage on linux with: %s" % command, 8)
                exitcode, output = j.system.process.execute(command, True, False)
                return output
            elif j.system.platformtype.isSolaris():
                command = 'ps -efo pcpu,pid |grep %d'%pid
                j.logger.log("getCPUusage on linux with: %s" % command, 8)
                exitcode, output = j.system.process.execute(command, True, False)
                cpuUsage = output.split(' ')[1]
                return cpuUsage
        except Exception:
            pass
        return 0

    def getMemoryUsage(self):
        """
        try to get memory usage, if it doesn't work will return 0i
        By default 0 for windows
        """
        try:
            pid = os.getpid()
            if j.system.platformtype.isWindows():
                # Not supported on windows
                return "0 K"
            elif j.system.platformtype.isLinux():
                command = "ps -o pmem %d | grep -E --regex=\"[0.9]\""%pid
                j.logger.log("getMemoryUsage on linux with: %s" % command, 8)
                exitcode, output = j.system.process.execute(command, True, False)
                return output
            elif j.system.platformtype.isSolaris():
                command = "ps -efo pcpu,pid |grep %d"%pid
                j.logger.log("getMemoryUsage on linux with: %s" % command, 8)
                exitcode, output = j.system.process.execute(command, True, False)
                memUsage = output.split(' ')[1]
                return memUsage
        except Exception:
            pass
        return 0

    def getUniqueMachineId(self):
        """
        will look for network interface and return a hash calculated from lowest mac address from all physical nics
        """
        nics = j.system.net.getNics()

        if j.system.platformtype.isWindows():
            order = ["local area", "wifi"]
            for item in order:
                for nic in nics:
                    if nic.lower().find(item) != -1:
                        return j.system.net.getMacAddress(nic)
        macaddr = []
        for nic in nics:
            if nic.find("lo") == -1:
                nicmac = j.system.net.getMacAddress(nic)
                macaddr.append(nicmac.replace(":", ""))
        macaddr.sort()
        if len(macaddr) < 1:
            raise RuntimeError("Cannot find macaddress of nics in machine.")
        return macaddr[0]

    def _setWriteExitcodeOnExit(self, value):
        if not j.basetype.boolean.check(value):
            raise TypeError
        j.logger.log("Setting j.application.writeExitcodeOnExit = %s"%str(value), 5)
        exitcodefilename = j.system.fs.joinPaths(j.dirs.tmpDir, 'qapplication.%d.exitcode'%os.getpid())
        if value and j.system.fs.exists(exitcodefilename):
            j.system.fs.remove(exitcodefilename)
        self._writeExitcodeOnExit = value

    def _getWriteExitcodeOnExit(self):
        if not hasattr(self, '_writeExitcodeOnExit'):
            return False
        return self._writeExitcodeOnExit

    writeExitcodeOnExit = property(fset=_setWriteExitcodeOnExit, fget=_getWriteExitcodeOnExit, doc="Gets / sets if the exitcode has to be persisted on disk")
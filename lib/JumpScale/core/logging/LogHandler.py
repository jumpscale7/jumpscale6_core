import itertools
import functools
from JumpScale import j
from .logtargets.LogTargetFS import LogTargetFS
from .logtargets.LogTargetStdOut import LogTargetStdOut
import re
import sys
import traceback
import time
from datetime import datetime

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except:
        from io import StringIO


# from logtargets.LogTargetFS import LogTargetFS
# from logtargets.LogTargetStdOut import LogTargetStdOut
#@todo P3 low prio, to get log handlers back working

SAFE_CHARS_REGEX = re.compile("[^ -~\n]")


def toolStripNonAsciFromText(text):
    """
    Filter out characters not between ' ' and '~' with an exception for
    newlines.

    @param text: text to strip characters from
    @type text: basestring
    @return: the stripped text
    @rtype: basestring
    """
    return SAFE_CHARS_REGEX.sub("", text)


class LogUtils(object):
    """
    Some log related utilities.
    """
    def trace(self, level=5, enabled=True):
        """
        Decorator factory. Use enabled to avoid the logging overhead when it's
        not needed. Do not the tracing can *not* be enabled or disabled at
        runtime.

        Typical usage:

        TRACING_ENABLED = True

        @j.logger.utils.trace(level=3, enabled=TRACING_ENABLED)
        def myFunc(arg1, arg2=12):
            ...

        @param level: level to log the calls on
        @type level: int
        @param enabled: whether or not to disable the tracing
        @type enabled: boolean
        @return: decorator factory
        @rtype: callable
        """

        if enabled:
            def decorator(func):
                """
                Decorator to log how and when the wrapped function is called.

                @param func: function to be wrapped
                @type func: callable
                @return: wrapped function
                @rtype: callable
                """
                @functools.wraps(func)
                def wrappedFunc(*args, **kwargs):
                    argiter = itertools.chain(args, ["%s=%s" % (k, v) for k, v in
                                                     kwargs.iteritems()])
                    descr = "%s(%s)" % (func.__name__, ", ".join(argiter))
                    j.logger.log("Calling " + descr, level)
                    try:
                        return func(*args, **kwargs)
                    finally:
                        j.logger.log("Called " + descr, level)
                return wrappedFunc
        else:
            def decorator(func):
                return func
        return decorator


class LogItem(object):
    def __init__(self, message="", category="", tags="", level=5, jid=0, parentjid=0, masterjid=0, private=False, epoch=0):
        self.message = message.strip().replace("\r\n", "/n").replace("\n", "/n")
        try:
            self.level = int(level)
        except:
            self.level=5
        self.category = category.replace(".", "_")
        if j.application.whoAmI:
            
            self.gid = j.application.whoAmI.gid
            self.nid = j.application.whoAmI.nid
            self.pid = j.application.whoAmI.pid
            if hasattr(j, 'core') and hasattr(j.core, 'grid') and hasattr(j.core.grid, 'aid'):
                self.aid = j.core.grid.aid
            else:
                self.aid = 0

        self.appname = j.application.appname
        self.tags = str(tags).strip().replace("\r\n", "/n").replace("\n", "/n").replace("|", "/|")
        self.jid = int(jid)
        self.parentjid = int(parentjid)
        self.masterjid = int(masterjid)
        self.epoch = int(epoch) or j.base.time.getTimeEpoch()
        j.logger.order += 1
        # if j.logger.order > 10000:
        #     j.logger.order = 1
        self.order = j.logger.order
        if private == True or int(private) == 1:
            self.private = 1
        else:
            self.private = 0

    def toJson(self):
        return j.db.serializers.ujson.dumps(self.__dict__)

    def __str__(self):
        if self.category!="":
            return "%s: %s" % (self.category.replace("_","."),self.message)
        else:
            ttime=time.strftime("%H:%M:%S: ", datetime.fromtimestamp(self.epoch).timetuple())
            message="%s %s %s%s" % (self.level, j.application.appname , ttime, self.message)
            return message

    __repr__ = __str__

class LogItemFromDict(LogItem):
    def __init__(self,ddict):
        self.__dict__=ddict

class LogHandler(object):
    def __init__(self):
        '''
        This empties the log targets
        '''
        self.utils = LogUtils()
        self.reset()

    def getLogObjectFromDict(self, ddict):
        return LogItemFromDict(ddict)

    def nologger(self, func):
        """
        Decorator to disable logging for a specific method (probably not thread safe)
        """
        def wrapper(*args, **kwargs):
            previousvalue = self.enabled
            self.enabled = False
            try:
                return func(*args, **kwargs)
            finally:
                self.enabled = previousvalue
        return wrapper

    def reset(self):
        self.maxlevel = 6
        self.consoleloglevel = 2
        self.consolelogCategories=[]
        self.lastmessage = ""
        # self.lastloglevel=0
        self.logs = []
        self.nolog = False

        self._lastcleanuptime = 0
        self._lastinittime = 9999999999  # every 5 seconds want to reinit the logger to make sure all targets which are available are connected

        self.logTargets = []
        self.inlog = False
        self.enabled = True
        self.clientdaemontarget = False
        self.order = 0

    def addConsoleLogCategory(self,category):
        category=category.lower()
        if category not in self.consolelogCategories:
            self.consolelogCategories.append(category)

    def addLogTargetStdOut(self):
        self.logTargetAdd(LogTargetStdOut())

    def addLogTargetElasticSearch(self):
        from .logtargets.LogTargetElasticSearch import LogTargetElasticSearch
        self.logTargetAdd(LogTargetElasticSearch('localhost'))

    def addLogTargetLocalFS(self):
        self.logTargetAdd(LogTargetFS())

    def setLogTargetLogForwarder(self, serverip=None):
        """
        there will be only logging to stdout (if q.loghandler.consoleloglevel set properly)
        & to the LogForwarder
        """
        from logtargets.LogTargetLogForwarder import LogTargetLogForwarder
        self.logs=[]
        self.inlog=False
        self.order=0
        self.clientdaemontarget = LogTargetLogForwarder(serverip)

    def disable(self):
        self.enabled = False
        for t in self.logTargets:
            t.close()
        self.logTargets = []

        if "console" in self.__dict__:
            self.console.disconnect()
            self.console = None

    def _init(self):
        """
        called by jumpscale
        """
        return  # need to rewrite logging
        self._lastinittime = 0
        self.nolog = True
        inifile = j.config.getInifile("main")
        if inifile.checkParam("main", "lastlogcleanup") == False:
            inifile.setParam("main", "lastlogcleanup", 0)
        self._lastcleanuptime = int(inifile.getValue("main", "lastlogcleanup"))
        self.nolog = False
        from logtargets.LogTargetToJumpScaleLogConsole import LogTargetToJumpScaleLogConsole
        self.logTargetAdd(LogTargetToJumpScaleLogConsole())

    def checktargets(self):
        """
        only execute this every 120 secs
        """

        # check which loggers are not working
        for target in self.logTargets:
            if target.enabled == False:
                try:
                    target.open()
                except:
                    target.enabled = False
        self.cleanup()

    def log(self, message, level=5, category="", tags="", jid=0, parentjid=0,masterjid=0, private=False):
        """
        send to all log targets
        """
        if not self.enabled:
            return
            
        log = LogItem(message=message, level=level, category=category, tags=tags, jid=jid, parentjid=parentjid,masterjid=masterjid, private=private)
        if not self.enabled:
            return

        if level < (self.consoleloglevel + 1):

            if self.consolelogCategories<>[]:
                for consolecat in self.consolelogCategories:
                    if log.category.find(consolecat)<>-1:
                        ccat=log.category
                        while len(ccat)<25:
                            ccat+=" "
                        ccat=ccat[0:25]
                        j.console.echo("%s :: %s"%(ccat,log.message), log=False)
                        break
            else:
                j.console.echo(str(log), log=False)
        
        if self.clientdaemontarget != False and self.clientdaemontarget.enabled:
            self.clientdaemontarget.log(log)

        else:
            # print "level:%s %s" % (level,message)

            if self.nolog:
                return
            # if message<>"" and message[-1]<>"\n":
            #    message+="\n"

            if level < self.maxlevel+1:
                if "transaction" in j.__dict__ and j.transaction.activeTransaction != None:
                    if len(j.transaction.activeTransaction.logs) > 250:
                        j.transaction.activeTransaction.logs = j.transaction.activeTransaction.logs[-200:]
                    j.transaction.activeTransaction.logs.append(log)

                self.logs.append(log)
                if len(self.logs) > 500:
                    self.logs = self.logs[-250:]

                # log to logtargets
                for logtarget in self.logTargets:
                    if (hasattr(logtarget, 'maxlevel') and level > logtarget.maxlevel):
                        continue
                    if (hasattr(logtarget, 'enabled') and not logtarget.enabled):
                        continue
                    logtarget.log(log)

    def exception(self, message, level=5):
        """
        Log `message` and the current exception traceback

        The current exception is retrieved automatically. There is no need to pass it.

        @param message: The message to log
        @type message: string
        @param level: The log level
        @type level: int
        """
        ei = sys.exc_info()
        sio = StringIO()
        traceback.print_exception(ei[0], ei[1], ei[2], None, sio)
        s = sio.getvalue()
        sio.close()
        self.log(message, level)
        self.log(s, level)

    def clear(self):
        self.logs = []

    def close(self):
        # for old logtargets
        for logtarget in self.logTargets:
            logtarget.close()

    def cleanup(self):
        """
        Cleanup your logs
        """
        if hasattr(self, '_fallbackLogger') and hasattr(self._fallbackLogger, 'cleanup'):
            self._fallbackLogger.cleanup()

        for logtarget in self.logTargets:
            if hasattr(logtarget, 'cleanup'):
                logtarget.cleanup()

    def logTargetAdd(self, logtarget):
        """
        Add a LogTarget object
        """
        count = self.logTargets.count(logtarget)
        if count > 0:
            return
        self.logTargets.append(logtarget)



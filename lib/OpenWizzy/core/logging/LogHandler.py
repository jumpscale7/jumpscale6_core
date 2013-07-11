import itertools
import functools
from OpenWizzy import o
import re
import sys
import traceback

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


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

        @o.logger.utils.trace(level=3, enabled=TRACING_ENABLED)
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
                    o.logger.log("Calling " + descr, level)
                    try:
                        return func(*args, **kwargs)
                    finally:
                        o.logger.log("Called " + descr, level)
                return wrappedFunc
        else:
            def decorator(func):
                return func
        return decorator


class LogItem(object):
    def __init__(self, message="", category="", tags="", level=5, jid=0, parentjid=0, masterjid=0, private=False, epoch=0):
        self.message = message.strip().replace("\r\n", "/n").replace("\n", "/n")
        self.level = int(level)
        self.category = category.replace(".", "_")
        if hasattr(o.application, 'whoAmI'):
            if len(o.application.whoAmI)==3:
                self.gid = o.application.whoAmI[0]
                self.nid = o.application.whoAmI[1]
                self.bid = 0
                self.aid = 0
                self.pid = 0
            elif len(o.application.whoAmI)==4:
                self.gid = o.application.whoAmI[0]
                self.bid = o.application.whoAmI[1]
                self.nid = o.application.whoAmI[2]
                self.pid = o.application.whoAmI[3]
                self.aid = o.core.grid.aid
            else:
                o.errorconditionhandler.raiseBug(message="whoAmi should be 3 or 4 items",category="log.id")

        self.tags = str(tags).strip().replace("\r\n", "/n").replace("\n", "/n").replace("|", "/|")
        self.jid = int(jid)
        self.parentjid = int(parentjid)
        self.masterjid = int(masterjid)
        self.epoch = int(epoch)
        if o.logger.clientdaemontarget<>False and self.epoch<>0:  #this  is for performance win, getting epoch is expensive
            self.epoch = o.base.time.getTimeEpoch()
        o.logger.order += 1
        if o.logger.order > 100000:
            o.logger.order = 1
        self.order = o.logger.order
        if private == True or int(private) == 1:
            self.private = 1
        else:
            self.private = 0

    def toJson(self):
        return o.db.serializers.ujson.dumps(self.__dict__)

    def __str__(self):
        if self.category<>"":
            return "%s: %s" % (self.category.replace("_","."),self.message)
        else:
            return self.message

    __repr__ = __str__

    # @staticmethod
    # def decodeLogMessage(cls, logmessage):
    #     """
    #     decode log to (message, level, category, tags)
    #     usage:
    #     message, level, category, tags=o.logger.decodeLogMessage(message)
    #     """
    #     epoch, level, category, tags, job, parentjid, private, message = logmessage.split("|", 7)
    #     return cls(message=message, category=category, tags=tags, job=job, parentjid=parentjid, private=private)


    # def toHRD(self):
    #     """
    #     decode log to human readable format (without time & tags)
    #     """
    #     return "#%s %s %s" % (self.level, self.category, self.message)

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

    def reset(self):
        self.maxlevel = 6
        self.consoleloglevel = 2
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

    def addLogTargetStdOut(self):
        self.logTargetAdd(LogTargetStdOut())

    def addLogTargetLocalFS(self):
        self.logTargetAdd(LogTargetFS())

    def setLogTargetLogForwarder(self, serverip=None):
        """
        there will be only logging to stdout (if q.loghandler.consoleloglevel set properly)
        & to the LogForwarder
        """
        from logtargets.LogTargetClientDaemon import LogTargetClientDaemon
        self.logs=[]
        self.inlog=False
        self.logTargets=[]
        self.order=0
        self.clientdaemontarget =LogTargetClientDaemon(serverip)

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
        called by openwizzy
        """
        return  # need to rewrite logging
        self._lastinittime = 0
        self.nolog = True
        inifile = o.config.getInifile("main")
        if inifile.checkParam("main", "lastlogcleanup") == False:
            inifile.setParam("main", "lastlogcleanup", 0)
        self._lastcleanuptime = int(inifile.getValue("main", "lastlogcleanup"))
        self.nolog = False
        from logtargets.LogTargetToPylabsLogConsole import LogTargetToPylabsLogConsole
        self.logTargetAdd(LogTargetToPylabsLogConsole())

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

        if self.clientdaemontarget != False:
            self.clientdaemontarget.log(log)

            if level < (self.consoleloglevel + 1):
                o.console.echo(str(log), log=False)
            return

        else:
            # print "level:%s %s" % (level,message)
            if level < (self.consoleloglevel + 1):
                o.console.echo(str(log), log=False)

            if self.nolog:
                return
            # if message<>"" and message[-1]<>"\n":
            #    message+="\n"

            if level < self.maxlevel+1:
                if "transaction" in o.__dict__ and o.transaction.activeTransaction != None:
                    if len(o.transaction.activeTransaction.logs) > 250:
                        o.transaction.activeTransaction.logs = o.transaction.activeTransaction.logs[-200:]
                    o.transaction.activeTransaction.logs.append(log)

                self.logs.append(log)
                if len(self.logs) > 500:
                    self.logs = self.logs[-250:]

                # log to logtargets
                for logtarget in self.logTargets:
                    if (hasattr(logtarget, 'maxlevel') and level > logtarget.maxlevel):
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



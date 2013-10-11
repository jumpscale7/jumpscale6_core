from JumpScale import j
import time
from datetime import datetime
import sys
import os
# import sitecustomize
import random
import stat

#@todo time is not local time, redo


class LogTargetFS(object):

    """
    log to local filesystem
    """

    def __init__(self):
        """
        """
        self.enabled = False
        # cannot use jumpscale primitives yet, not enabled yet
        self.name = "file"
        self.fileHandle = None
        self.logopenTime = 0
        self.logopenNrlines = 0
        self.logfile = ""
        self._initializing = False
        self.agentid = j.application.agentid
        self.appname = j.application.appname.split(':')[0]
        self.lastappstatus = j.application.state
        self._queue = []
        # except:
            # self.agentid="unknown"
        if j.system.platformtype.isWindows():
            logdir = os.path.join(j.system.windows.getTmpPath(), "QBASEVAR")
            if not os.path.isdir(logdir):
                os.mkdir(logdir)
            logdir = os.path.join(logdir, "LOGSTARTUP")
            if not os.path.isdir(logdir):
                os.mkdir(logdir)

        self.enabled = True  # self.checkTarget()

        # j.base.time.getLocalTimeHRForFilesystem()

    def _gettime(self):
        return int(time.time())

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if not self.fileHandle or self.fileHandle.closed or not os.path.isfile(self.logfile):
            return self.open()
        return True

    def log(self, log, skipQueue=False):
        """
        """
        if not self._is_initialized():
            skip = self._initialize()
            if skip:
                self._queue.append(log)
                return
        if not skipQueue:
            for queitem in self._queue:
                self.log(queitem, True)
            self._queue = list()

        if not self.enabled:
            self.enabled = self.checkTarget()

        ttime = time.strftime("%H:%M:%S: ", datetime.fromtimestamp(log.epoch).timetuple())
        message = "%s %s %s%s" % (log.level, j.application.appname, ttime, log.message)

        appLogname = j.application.appname.split(':')[0]

        # print self._gettime()>(self.logopenTime+60)
        if self._config['main']['logrotate_enable'] == 'True':
            if self._gettime() > (self.logopenTime + int(self._config['main']['logrotate_time'])) \
                or self.logopenNrlines > int(self._config['main']['logrotate_number_of_lines']) \
                or self.appname != appLogname:

                # print "NEWLOG"
                self.rotate()
                self.logopenTime = self._gettime()
                self.logopenNrlines = 0
                self.lastappstatus = j.application.state

        try:
            # print "log:%s" % message
            self.fileHandle.write("%s\n" % message)
            self.fileHandle.flush()
        except:
            self.enabled = False
            # print "LOG:%s" %message
            return False

        return True

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, LogTargetFS):
            return False
        return True

    def open(self):
        if not self._is_initialized():
            self._initialize()

        appLogname = j.application.appname.split(':')[0]

        if appLogname != self.appname:
            self.appname = appLogname

        if not os.path.isdir(j.dirs.logDir):
            os.makedirs(j.log.logDir, 0o755)
        logfile = os.path.join(j.dirs.logDir, appLogname)
        self.logfile = "%s.log" % logfile
        try:
            self.fileHandle = open(self.logfile, 'a')
        except:
            return False
        self.logopenTime = os.stat(self.logfile)[stat.ST_CTIME]
        return True

    def rotate(self):
        cnt = 1
        while True:
            filename = os.path.join(j.dirs.logDir, "%s.log.%d" % (self.appname, cnt))
            if not j.system.fs.exists(filename):
                break
            cnt += 1
        if self.logfile and os.path.exists(self.logfile):
            os.rename(self.logfile, filename)
        self.close()
        self.open()

    def close(self):
        if self.fileHandle:
            attempts = 0
            max_attempts = 5
            close_error = None

            while attempts < max_attempts:
                attempts += 1
                try:
                    self.fileHandle.close()
                except IOError as ioe:
                    if ioe.errno is None:
                        # 'close() called during concurrent operation on the same file object'
                        # Probably a thread is trying to write to the log file.
                        if close_error is None:
                            close_error = ioe
                        continue
                    raise
                else:
                    break
                finally:
                    # We really don't want the file handle to leak
                    self.fileHandle = None
            if attempts > 1:
                sys.stderr.write(
                    'Unable to close log file on first attempt, retrying '
                    'retrying: %s\n' % (close_error,))
                if attempts == max_attempts:
                    sys.stderr.write(
                        'Unable to close log file after %d attempts.\n'
                        % (max_attempts,))
            self.fileHandle = None

    def cleanup(self):

        if self.__dict__.has_key("_config"):
            if self._config['main']['logremove_enable'] == 'True':

                if int(self._lastcleanuptime) <= (j.base.time.getTimeEpoch() - int(self._config['main']['logremove_check'])):

                    self._lastcleanuptime = j.base.time.getTimeEpoch()
                    self.nolog = True
                    inifile = j.config.getInifile("main")
                    inifile.setParam("main", "lastlogcleanup", self._lastcleanuptime)
                    files = j.system.fs.listFilesInDir(
                        j.system.fs.joinPaths(j.dirs.logDir, 'jumpscalelogs'),
                        recursive=True,
                        maxmtime=(j.base.time.getTimeEpoch() - int(self._config['main']['logremove_age'])))

                    for filepath in files:
                        if j.system.fs.exists(filepath):
                            try:
                                j.system.fs.remove(filepath)
                            except Exception as ex:
                                pass  # We don't want to fail on logging

                    self.nolog = False

    def _is_initialized(self):
        return hasattr(self, '_config') and self._config and hasattr(self, '_lastcleanuptime')

    def _initialize(self):
        """
        Initialize logtarget config

        As we are in the initialization phase of the logging framework, we can't use anything
        using the logging framework.
        """
        if j.application.state != j.enumerators.AppStatusType.RUNNING or self._initializing:
            return True
        self._initializing = True

        mainfile = j.config.getInifile("main")
        if 'main' in mainfile.getSections() and mainfile.getValue('main', 'lastlogcleanup'):
            self._lastcleanuptime = mainfile.getValue('main', 'lastlogcleanup')
        else:
            self._lastcleanuptime = -1

        # Check if we should rotate logfiles

        cfg_defaults = {'main': {'logremove_enable': 'True',
                                 'logrotate_enable': 'True',
                                 'logrotate_number_of_lines': '5000',
                                 'logremove_age': '432000',
                                 'logrotate_time': '86400', # one day
                                 'logremove_check': '86400'}}

        cfg = None
        if 'logtargetfs' in j.config.list():
            logtargetfs_file = j.config.getInifile("logtargetfs")
            cfg = logtargetfs_file.getFileAsDict()

        if not cfg or not 'main' in cfg.keys():
            cfg = cfg_defaults

        self._config = cfg

        for k, v in cfg_defaults['main'].iteritems():
            if not self._config['main'].has_key(k) or self._config['main'].get(k) == None:
                self._config['main'][k] = v

        self.enabled = self.checkTarget()
        self._initializing = False


# Config
# from JumpScale.core.config import ConfigManagementItem, ItemSingleClass
#
# class LogTargetFSConfigManagementItem(ConfigManagementItem):
#    """
#    Configuration of a Cloud API connection
#    """
# (MANDATORY) CONFIGTYPE and DESCRIPTION
#    CONFIGTYPE = "logtargetfs"
#    DESCRIPTION = "JumpScale Filesystem Logtarget"
#    KEYS ={"logrotate_enable":"",
#           "logrotate_number_of_lines":"",
#           "logrotate_time":"",
#           "logremove_enable":"",
#           "logremove_age":"",
#           "logremove_check":""
#           }
# MANDATORY IMPLEMENTATION OF ASK METHOD
#    def ask(self):
#        self.dialogAskYesNo('logrotate_enable', 'Enable automatic rotation of logfiles', True)
#        if self.params['logrotate_enable']:
#            self.dialogAskInteger('logrotate_number_of_lines', 'Max number of lines per file', 5000)
#            self.dialogAskInteger('logrotate_time', 'Max period of logging per files in seconds', 86400)
#        self.dialogAskYesNo('logremove_enable', 'Enable automatic removal of logfiles', True)
#        if self.params['logremove_enable']:
#            self.dialogAskInteger('logremove_age', 'Max age of logfiles in seconds', 432000)
#            self.dialogAskInteger('logremove_check', 'Interval to remove files older than max age', 86400)
#
#
# OPTIONAL CUSTOMIZATIONS OF CONFIGURATION
#
#    def show(self):
#        """
#        Optional customization of show() method
#        """
# Here we do not want to show the password, so a customized show() method
#        j.gui.dialog.message(self.params)
#
#    def retrieve(self):
#        """
#        Optional implementation of retrieve() method, to be used by find()
#        """
#        return self.params
#
#

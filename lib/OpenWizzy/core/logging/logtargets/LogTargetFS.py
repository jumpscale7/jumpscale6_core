from OpenWizzy import o
import time
from datetime import datetime
import sys,os
#import sitecustomize
import random

#@todo time is not local time, redo

class LogTargetFS(object):
    """
    log to local filesystem
    """

    def __init__(self):
        """
        """
        self.enabled = False
        #cannot use openwizzy primitives yet, not enabled yet
        self.name = "file"
        self.fileHandle = None
        self.logopenTime=self._gettime()
        self.logopenNrlines=0
        self.logfile=""
        self._initializing = False
        self.agentid=o.application.agentid
        self.appname=o.application.appname.split(':')[0]
        self.lastappstatus=o.application.state
        #except:
            #self.agentid="unknown"
        if o.system.platformtype.isWindows():
            logdir=os.path.join(o.system.windows.getTmpPath(),"QBASEVAR")
            if not os.path.isdir(logdir):
                os.mkdir(logdir)
            logdir=os.path.join(logdir,"LOGSTARTUP")
            if not os.path.isdir(logdir):
                os.mkdir(logdir)
        else:
            logdir=os.path.join(o.dirs.baseDir,"var",'log',"openwizzylogs")
        
        if not os.path.isdir(logdir):
            os.mkdir(logdir)
        if os.path.isdir(logdir)==False:
            os.mkdir(logdir)
            
        self.enabled = True #self.checkTarget()

        #o.base.time.getLocalTimeHRForFilesystem()

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

    def log(self, log):
        """
        """
        if not self._is_initialized():
            skip=self._initialize()
            if skip:
                return
        
        if not self.enabled:
            self.enabled = self.checkTarget()

        ttime=time.strftime("%H:%M:%S: ", datetime.fromtimestamp(log.epoch).timetuple())
        message="%s %s %s%s" % (log.level, o.application.appname , ttime, log.message)

        appLogname = o.application.appname.split(':')[0]

        ##print self._gettime()>(self.logopenTime+60)
        if self._config['main']['logrotate_enable'] == 'True':
            if self._gettime() > (self.logopenTime + int(self._config['main']['logrotate_time'])) \
                or self.logopenNrlines > int(self._config['main']['logrotate_number_of_lines']) \
                or self.appname <> appLogname \
                or o.application.state <> self.lastappstatus:
                
                ##print "NEWLOG"
                self.close()
                self.open()
                self.logopenTime=self._gettime()
                self.logopenNrlines=0
                self.lastappstatus=o.application.state

        try:
            #print "log:%s" % message
            self.fileHandle.write("%s\n"%message)
            self.fileHandle.flush()
        except:
            self.enabled = False
            ##print "LOG:%s" %message
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

        appLogname = o.application.appname.split(':')[0]
        logdir=os.path.join(o.dirs.varDir,'log',"openwizzylogs",appLogname)

        if appLogname<>self.appname:
            self.appname=appLogname

        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        filename=time.strftime("%b_%d--%H_%M_%S", time.gmtime())
        logfile=os.path.join(logdir,"%s_%s"%(filename,o.application.state))
        filenum = 1
        if os.path.isfile("%s.log" % logfile):
            logfile = "%s_%s"%(logfile, random.randint(1,10000))
            filenum += 1

        self.logfile="%s.log" % logfile
        #print "logfile:%s" % self.logfile
        try:
            self.fileHandle = open(self.logfile, 'a')
        except:
            return False

        return True

    def close(self):
        if self.fileHandle:
            attempts = 0
            max_attempts = 5
            close_error = None

            while attempts < max_attempts:
                attempts += 1
                try:
                    self.fileHandle.close()
                except IOError, ioe:
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
              
                if int(self._lastcleanuptime) <= (o.base.time.getTimeEpoch() - int(self._config['main']['logremove_check'])):
            
                    self._lastcleanuptime=o.base.time.getTimeEpoch()
                    self.nolog=True
                    inifile=o.config.getInifile("main")
                    inifile.setParam("main","lastlogcleanup",self._lastcleanuptime)
                    files= o.system.fs.listFilesInDir( \
                                o.system.fs.joinPaths(o.dirs.logDir, 'openwizzylogs'), \
                                recursive=True, \
                                maxmtime=(o.base.time.getTimeEpoch() - int(self._config['main']['logremove_age'])))
                    
                    for filepath in files:
                        if o.system.fs.exists(filepath):
                            try:
                                o.system.fs.removeFile(filepath)
                            except Exception, ex:
                                pass # We don't want to fail on logging
                
                    self.nolog=False
                
    def _is_initialized(self):
        return hasattr(self, '_config') and self._config and hasattr(self, '_lastcleanuptime')
    
    def _initialize(self):
        
        """
        Initialize logtarget config

        As we are in the initialization phase of the logging framework, we can't use anything
        using the logging framework.
        """
        if o.application.state != o.enumerators.AppStatusType.RUNNING or self._initializing:
            return True
        self._initializing = True
        
        mainfile = o.config.getInifile("main")
        if 'main' in mainfile.getSections() and mainfile.getValue('main', 'lastlogcleanup'):
            self._lastcleanuptime = mainfile.getValue('main', 'lastlogcleanup')
        else:
            self._lastcleanuptime = -1
 
        # Check if we should rotate logfiles
        """
        In [6]: o.config.getConfig('logtargetfs')                                                                                                                                                     
        {'main': {'logremove_enable': 'True',
                  'logrotate_enable': 'True',
                  'logrotate_number_of_lines': '5000',
                  'logremove_age': '432000',
                  'logrotate_time': '60',
                  'logremove_check': '86400'}}
        """
        
        cfg_defaults = {'main': {'logremove_enable': 'True',
                  'logrotate_enable': 'True',
                  'logrotate_number_of_lines': '5000',
                  'logremove_age': '432000',
                  'logrotate_time': '60',
                  'logremove_check': '86400'}}
        
        cfg = None
        if 'logtargetfs' in o.config.list():
            logtargetfs_file = o.config.getInifile("logtargetfs")
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
#from OpenWizzy.core.config import ConfigManagementItem, ItemSingleClass
#
#class LogTargetFSConfigManagementItem(ConfigManagementItem):
#    """
#    Configuration of a Cloud API connection
#    """
#    # (MANDATORY) CONFIGTYPE and DESCRIPTION
#    CONFIGTYPE = "logtargetfs"
#    DESCRIPTION = "Pylabs Filesystem Logtarget"
#    KEYS ={"logrotate_enable":"",
#           "logrotate_number_of_lines":"",
#           "logrotate_time":"",
#           "logremove_enable":"",
#           "logremove_age":"",
#           "logremove_check":""           
#           }
#    # MANDATORY IMPLEMENTATION OF ASK METHOD
#    def ask(self):
#        self.dialogAskYesNo('logrotate_enable', 'Enable automatic rotation of logfiles', True)
#        if self.params['logrotate_enable']:
#            self.dialogAskInteger('logrotate_number_of_lines', 'Max number of lines per file', 5000)
#            self.dialogAskInteger('logrotate_time', 'Max period of logging per files in seconds', 60)
#        self.dialogAskYesNo('logremove_enable', 'Enable automatic removal of logfiles', True)
#        if self.params['logremove_enable']:
#            self.dialogAskInteger('logremove_age', 'Max age of logfiles in seconds', 432000)
#            self.dialogAskInteger('logremove_check', 'Interval to remove files older than max age', 86400)
#            
#            
#    #  OPTIONAL CUSTOMIZATIONS OF CONFIGURATION
#
#    def show(self):
#        """
#        Optional customization of show() method
#        """
#        # Here we do not want to show the password, so a customized show() method
#        o.gui.dialog.message(self.params)
#        
#    def retrieve(self):
#        """
#        Optional implementation of retrieve() method, to be used by find()
#        """
#        return self.params
#
#      

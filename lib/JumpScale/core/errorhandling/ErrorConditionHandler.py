import sys
import traceback
import string
import inspect
import imp

from JumpScale import j

from ErrorConditionObject import ErrorConditionObject

class BaseException(Exception):
    def __init__(self, message, eco=None):
        self.message = message
        self.eco = eco

    def __str__(self):
        if self.eco:
            return str(j.errorconditionhandler.getErrorConditionObject(self.eco))
        return "Unexpected Error Happened"

    __repr__ = __str__

class HaltException(BaseException):
    pass

class ErrorConditionHandler():
    
    def __init__(self,haltOnError=True,storeErrorConditionsLocal=True):
        self._blacklist = None
        self.lastAction=""
        self.haltOnError=haltOnError     
        self.setExceptHook()
        self.lastEco=None

    @property
    def blacklist(self):
        if self._blacklist is None:
            key = 'application.eco.blacklist'
            if j.application.config.exists(key):
                self._blacklist = j.application.config.getList(key)
            else:
                self._blacklist = list()
        return self._blacklist
        
    def toolStripNonAsciFromText(text):
        return string.join([char for char in str(text) if ((ord(char)>31 and ord(char)<127) or ord(char)==10)],"")        
        
    def setExceptHook(self):
        sys.excepthook = self.excepthook
        self.inException=False


    def _handleRaise(self, type, level, message,category="", pythonExceptionObject=None,pythonTraceBack=None,msgpub="",tags=""):
        if pythonExceptionObject<>None:
            eco=self.parsePythonErrorObject(pythonExceptionObject,level=level,message=message)            
            eco.category=category
        else:
            eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=level) 
            eco.getBacktrace()

        eco.tags=tags
        eco.type=int(type)
        self.processErrorConditionObject(eco, centralsentry=True)
        return eco

    def raiseBug(self, message,category="", pythonExceptionObject=None,pythonTraceBack=None,msgpub="",die=True,tags="", level=j.enumerators.ErrorConditionLevel.CRITICAL):
        """
        use this to raise a bug in the code, this is the only time that a stacktrace will be asked for
        level will be Critical
        @param message is the error message which describes the bug
        @param msgpub is message we want to show to endcustomers (can include a solution)
        @param category is a dot notation to give category for the error condition
        @param pythonExceptionObject is the object as it comes from a try except statement

        try:
            ##do something            
        except Exception,e:
            j.errorconditionhandler.raiseBug("an error",category="exceptions.init",e)
        
        """
        type = j.enumerators.ErrorConditionType.BUG
        eco = self._handleRaise(type, level, message, category, pythonExceptionObject, pythonTraceBack, msgpub, tags)
        if die:                     
            self.halt(eco.errormessage, eco)

    raiseCritical = raiseBug

    def raiseWarning(self, message,category="", pythonExceptionObject=None,pythonTraceBack=None,msgpub="",tags=""):
        """
        use this to raise a bug in the code, this is the only time that a stacktrace will be asked for
        @param message is the error message which describes the bug
        @param msgpub is message we want to show to endcustomers (can include a solution)
        @param category is a dot notation to give category for the error condition
        @param pythonExceptionObject is the object as it comes from a try except statement

        try:
            ##do something            
        except Exception,e:
            j.errorconditionhandler.raiseBug("an error",category="exceptions.init",e)
        
        """
        level = j.enumerators.ErrorConditionLevel.WARNING
        self.raiseBug(message, category, pythonExceptionObject, pythonTraceBack, msgpub, False, tags, level)
        
    def raiseOperationalCritical(self, message="", category="",msgpub="",die=True,tags="",eco=None,extra=None):
        """
        use this to raise an operational issue about the system
        @param message is message we want to use for operators
        @param msgpub is message we want to show to endcustomers (can include a solution)
        @param category is a dot notation to give category for the error condition
        """
        if not eco:
            eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=1,\
                                         type=j.enumerators.ErrorConditionType.OPERATIONS)
            eco.tags=tags
        else:
            eco.type=int(j.enumerators.ErrorConditionType.OPERATIONS)
            eco.level=1

        if eco<>None:
            eco.errormessage=eco.errormessage.strip("\"")
        if extra<>None:
            eco.extra=extra
        
        self.processErrorConditionObject(eco,tostdout=False, centralsentry=True)
     
        msg = eco.errormessage 
        if j.application.debug:
            msg=str(eco)

        print "\n#########   Operational Critical Error    #################\n%s\n###########################################################\n"% msg
        print 
        if die:
            self.halt(str(eco), eco)

    def raiseRuntimeErrorWithEco(self,eco,tostdout=False):
        message=""
        if eco.tags<>"":
            message+="((tags:%s))\n"%eco.tags
        if eco.category<>"":
            message+="((category:%s))\n"%eco.category
        message+="((type:%s))\n"%str(eco.type)
        message+="((level:%s))\n"%eco.level
        if tostdout==False:
            message+="((silent))\n"
        raise RuntimeError(message)

    def raiseOperationalWarning(self, message="", category="",msgpub="",tags="",eco=None):
        level = j.enumerators.ErrorConditionLevel.WARNING.level
        if not eco:
            eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=level,\
                                         type=j.enumerators.ErrorConditionType.OPERATIONS)
            eco.tags=tags
        else:
            eco.type=int(j.enumerators.ErrorConditionType.OPERATIONS)
            eco.level=level
        self.processErrorConditionObject(eco, centralsentry=True)
        
    def raiseInputError(self, message="", category="input",msgpub="",die=True ,backtrace="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=1,type=j.enumerators.ErrorConditionType.INPUT)
        eco.tags=tags
        if backtrace:
            eco.backtrace=backtrace
        self.processErrorConditionObject(eco,tostdout=False)
   
        if j.application.debug:
            print eco
        else:
            print "***INPUT ERROR***"
            if category<>None:
                print "category:%s"%category     
            print message

        if die:
            self.halt(eco.errormessage, eco)
        
    def raiseMonitoringError(self, message, category="",msgpub="",die=False,tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=1,type=j.enumerators.ErrorConditionType.MONITORING)
        eco.tags=tags
        self.processErrorConditionObject(eco)
        if die:
            self.halt(eco.description, eco)
        
    def raisePerformanceError(self, message, category="",msgpub="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=1,type=j.enumerators.ErrorConditionType.PERFORMANCE)
        eco.tags=tags
        if die:
            self.halt(eco.description, eco)
        
    def getErrorConditionObject(self,ddict={},msg="",msgpub="",category="",level=1,type=0,tb=None):
        """
        @data is dict with fields of errorcondition obj
        returns only ErrorConditionObject which should be used in jumpscale to define an errorcondition (or potential error condition)
        
        """                
        errorconditionObject= ErrorConditionObject(ddict=ddict,msg=msg,msgpub=msgpub,level=level,category=category,type=type,tb=tb)                
        return errorconditionObject        
  
    def processPythonExceptionObject(self,pythonExceptionObject,ttype=None, tb=None,level=1,message="",sentry=True):
        """ 
        how to use
        
        try:
            ##do something            
        except Exception,e:
            j.errorconditionhandler.processpythonExceptionObject(e)
            
        @param pythonExceptionObject is errorobject thrown by python when there is an exception
        @param ttype : is the description of the error, can be None
        @param tb : can be a python data object for traceback, can be None
        
        @return [ecsource,ecid,ecguid]
        
        the errorcondition is then also processed e.g. send to local logserver and/or stored locally in errordb
        see j.errorconditionhandler.processErrorConditionObject how to use this and overrule the behaviour
        """        
        obj=self.parsePythonErrorObject(pythonExceptionObject,ttype, tb,level,message)

        return self.processErrorConditionObject(obj,sentry=sentry)
        
    def parsePythonErrorObject(self,pythonExceptionObject,ttype=None, tb=None,level=1,message=""):
        
        """ 
        how to use
        
        try:
            ##do something            
        except Exception,e:
            eco=j.errorconditionhandler.parsePythonErrorObject(e)

        eco is jumpscale internal format for an error 
        next step could be to process the error objecect (eco) e.g. by j.errorconditionhandler.processErrorConditionObject(eco)
            
        @param pythonExceptionObject is errorobject thrown by python when there is an exception
        @param ttype : is the description of the error, can be None
        @param tb : can be a python data object for traceback, can be None
        
        @return a ErrorConditionObject object as used by jumpscale (should be the only type of object we send around)
        """
        if isinstance(pythonExceptionObject, BaseException):
            return self.getErrorConditionObject(pythonExceptionObject.eco)

        if tb==None:
            ttype, exc_value, tb=sys.exc_info()
        try:
            message2=pythonExceptionObject.message
            if message2.strip()=="":
                message2=str(pythonExceptionObject)
        except:
            message2=str(pythonExceptionObject)
            
        if message2.find("((")<>-1:
            tag=j.codetools.regex.findOne("\(\(.*\)\)",message2)         
        else:
            tag=""
            
        message+=message2
        
        if ttype<>None:
            try:
                type_str=str(ttype).split("exceptions.")[1].split("'")[0]
            except:
                type_str=str(ttype)
        else:
            type_str=""
            
        if type_str.lower().find("exception")==-1:
            message="%s: %s" % (type_str,message)
        

        errorobject=self.getErrorConditionObject(msg=message,msgpub="",level=level,tb=tb)

        try:
            import ujson as json
        except:
            import json

        errorobject.exceptioninfo = json.dumps({'message': pythonExceptionObject.message})

        errorobject.exceptionclassname = pythonExceptionObject.__class__.__name__
        module = inspect.getmodule(pythonExceptionObject)
        errorobject.exceptionmodule = module.__name__ if module else None
        
        # errorobject.tb=tb

        # try:
        try:
            backtrace = "~ ".join([res for res in traceback.format_exception(ttype, pythonExceptionObject, tb)])
            if len(backtrace)>10000:
                backtrace=backtrace[:10000]
            errorobject.backtrace=backtrace
        except:
            print "ERROR in trying to get backtrace"

        # except Exception,e:
        #     print "CRITICAL ERROR in trying to get errorobject, is BUG, please check (ErrorConditionHandler.py on line 228)"
        #     print "error:%s"%e
        #     sys.exit()

        try:
            errorobject.funcfilename=tb.tb_frame.f_code.co_filename
        except:
            pass
                        
        return errorobject        

    def reRaiseECO(self, eco):
        import json
        if eco.exceptionmodule:
            mod = imp.load_package(eco.exceptionmodule, eco.exceptionmodule)
        else:
            import __builtin__ as mod
        Klass = getattr(mod, eco.exceptionclassname, RuntimeError)
        exc = Klass(eco.errormessage)
        for key, value in json.loads(eco.exceptioninfo).iteritems():
            setattr(exc, key, value)
        raise exc

    def parsepythonExceptionObject(self,*args,**kwargs):
        raise RuntimeError("Do not use .parsepythonExceptionObject method use .parsePythonErrorObject")

    def excepthook(self, ttype, pythonExceptionObject, tb):
        """ every fatal error in jumpscale or by python itself will result in an exception
        in this function the exception is caught.
        This routine will create an errorobject & escalate to the infoserver
        @ttype : is the description of the error
        @tb : can be a python data object or a Event
        """        
        if str(pythonExceptionObject).find("**halt**")<>-1:
            j.application.stop()

        # print "jumpscale EXCEPTIONHOOK"
        if self.inException:
            print "ERROR IN EXCEPTION HANDLING ROUTINES, which causes recursive errorhandling behaviour."
            print pythonExceptionObject
            return 

        self.inException=True
        print "ERROR"
        print pythonExceptionObject

        errorobject=self.parsePythonErrorObject(pythonExceptionObject,ttype=ttype,tb=tb)

        if self.lastAction<>"":
            j.logger.log("Last action done before error was %s" % self.lastAction)
        self._dealWithRunningAction()      
        self.inException=False             
        self.processErrorConditionObject(errorobject,sentry=True)

        if j.application.shellconfig.interactive:
            return self.escalateBugToDeveloper(errorobject,tb)

    def checkErrorIgnore(self,eco):
        if j.application.debug:
            ignorelist = []
        else:
            ignorelist=["KeyboardInterrupt"]
        for item in ignorelist:
            if eco.errormessage.find(item)<>-1:
                return True
        if j.application.appname in self.blacklist:
            return True
        return False

    def getFrames(self,tb=None):

        def _getitem_from_frame(f_locals, key, default=None):
            """
            f_locals is not guaranteed to have .get(), but it will always
            support __getitem__. Even if it doesnt, we return ``default``.
            """
            try:
                return f_locals[key]
            except Exception:
                return default

        if tb==None:
            ttype,msg,tb=sys.exc_info()

        if tb==None:
            frames=[(item[0],item[2]) for item in inspect.stack()]
        else:
            frames=[]
            while tb: #copied from sentry raven lib (BSD license)
                # support for __traceback_hide__ which is used by a few libraries
                # to hide internal frames.
                f_locals = getattr(tb.tb_frame, 'f_locals', {})
                if not _getitem_from_frame(f_locals, '__traceback_hide__'):
                    frames.append((tb.tb_frame, getattr(tb, 'tb_lineno', None)))
                tb = tb.tb_next        
            frames.reverse()  

        result=[]
        ignore=["ipython","errorcondition","loghandler","errorhandling"]
        for frame,linenr in frames:
            name=frame.f_code.co_filename
            # print "RRR:%s %s"%(name,linenr)
            name=name.lower()
            toignore=False
            for check in ignore:
                if name.find(check)<>-1:
                    toignore=True
            if not toignore:
                result.append((frame,linenr))

        return result

    def getErrorTraceKIS(self,tb=None):
        out=[]
        nr=1
        filename0="unknown"
        linenr0=0
        func0="unknown"
        frs=self.getFrames(tb=tb)
        frs.reverse()
        for f,linenr in frs:            
            try:
                code,linenr2=inspect.findsource(f)
            except IOError:
                continue
            start=max(linenr-10,0)
            stop=min(linenr+4,len(code))
            code2="".join(code[start:stop])
            finfo=inspect.getframeinfo(f)
            linenr3=linenr-start-1
            out.append((finfo.filename,finfo.function,linenr3,code2,linenr))
            if nr==1:
                filename0=finfo.filename
                linenr0=linenr
                func0=finfo.function

        return out,filename0,linenr0,func0

    def processErrorConditionObject(self,errorConditionObject,tostdout=True,sentry=True,modulename=None, centralsentry=False):
        """
        a errorObject gets processed which means stored locally or forwarded to a logserver or both
        @return [ecsource,ecid,ecguid]

        you can overrule this behaviour by changing at rutime this function with a new one e.g. following code could work

        ### code:
        def myProcessErrorConditionObject(eco):
            print eco

        j.errorconditionhandler.processErrorConditionObject=myProcessErrorConditionObject
        ###

        now there would be no further processing appart from priting the errorcondition object (eco)

        """
        eco=errorConditionObject

        eco.toAscii()

        if self.checkErrorIgnore(eco):
            return

        if j.system.net.tcpPortConnectionTest("127.0.0.1",7768):
            if len(eco.guid)>30:
                #means is guid, will try to make more meaningfull guid
                import JumpScale.baselib.redis
                redis=j.clients.redis.getRedisClient("127.0.0.1",7768)
                incrkey="%s_%s"%(eco.gid,eco.nid)
                eco.id=redis.incr("eco:incr:%s"%incrkey,1)
                eco.guid = "%s_%s_%s"%(eco.gid,eco.nid,eco.id)

        if len(eco.guid)>30:
            pass
            #@todo debug
            

        if j.logger.logTargetLogForwarder and j.logger.logTargetLogForwarder.enabled:
            j.logger.logTargetLogForwarder.logECO(eco)

        if tostdout:
            print eco

        if sentry and j.application.config.exists("sentry.server"):
            self.sendEcoToSentry(eco, modulename)
        if centralsentry:
            keys = set( key.split('.')[0] for key in j.application.config.prefix('sentry') )
            keys.discard('sentry')
            for othersentry in keys:
                self.sendEcoToSentry(eco, modulename, othersentry)

        return eco

    def sendEcoToSentry(self, eco, modulename=None, hrdprefix='sentry'):
        extra={}
        tb=eco.tb

        if eco.__dict__.has_key("frames"):
            frames=eco.frames
        else:
            frames=[]
        if eco.backtrace<>"":
            extra["tb"]=eco.backtrace

        if eco.backtraceDetailed<>"":
            extra["tb_detail"]=eco.backtraceDetailed

        if hasattr(eco,"extra") and eco.extra<>None:
            extra["details"]=eco.extra

        extra["category"]=eco.category
        try:
            ttype = str(j.enumerators.ErrorConditionType.getByLevel(int(eco.type)))
        except Exception,e:
            ttype=j.enumerators.ErrorConditionType.UNKNOWN
        try:
            level = str(j.enumerators.ErrorConditionLevel.getByLevel(int(eco.level)))
        except Exception,e:
            level=j.enumerators.ErrorConditionLevel.UNKNOWN
        
        self.sendMessageToSentry(modulename=modulename,message=eco.errormessage,ttype=ttype,frames=frames,tags=None,\
            extra=extra,level=level,tb=tb, hrdprefix=hrdprefix)

    def sendMessageToSentry(self,modulename,message,ttype="bug",tags=None,extra={},level="error",tb=None,frames=[],backtrace="", hrdprefix="sentry"):
        """
        @param level
            fatal
            error
            warning
            info
            debug

        """

        if j.application.config.exists("%s.server" % hrdprefix):
            import requests
            try:
                import ujson as json
            except:
                import json
            import uuid
            import datetime
            server=j.application.config.get("%s.server" %hrdprefix)
            pub=j.application.config.get("%s.public.key" % hrdprefix)
            secret=j.application.config.get("%s.secret.key" % hrdprefix)
            port=j.application.config.getInt("%s.port" % hrdprefix)
            default=j.application.config.get("%s.project" % hrdprefix)
            url='http://%s:%s/'%(server,port)
            exc={}
            exc["type"]=ttype
            exc["value"]=message

            def ignore(modulename):
                if modulename.strip()=="":
                    return True
                toignore=["errorhandling"]
                for check in toignore:
                    if modulename.find(check)<>-1:
                        return True
                return False
                

            if modulename==None:
                modulename="appname:%s"%(j.application.appname)
                try:
                    if frames==[]:
                        frames=self.getFrames(tb)
                    frame=frames.pop()[0]
                    modulename=""
                    while ignore(modulename):                    
                        modulename=inspect.getmodule(frame)
                        if modulename==None or str(modulename).strip()=="":
                            modulename=inspect.getmodulename(frame.f_code.co_filename)
                        modulename=str(modulename)
                        modulename=modulename.replace("<module ","").replace("'","").replace(".pyc","").replace(">","")
                        try:
                            modulename=modulename.split("from")[0].strip()
                        except:
                            pass
                        if len(frames)>0:
                            frame=frames.pop()[0]
                        else:
                            modulename="appname:%s"%(j.application.appname)
                    if modulename.find("appname")==-1:
                        modulename="appname:%s / %s"%(j.application.appname,modulename)
                except Exception,e:
                    modulename="appname:%s"%(j.application.appname)  

                
            exc["module"]=modulename
            exc=[exc]
            if tags==None:
                tags={}
            else:
                tags=j.core.tags.getObject(tags)
                tags=tags.getDict()
            tags['type'] = ttype

            data={}
            data["event_id"]=uuid.uuid4().hex
            data["culprit"]=modulename
            data["timestamp"]=str(datetime.datetime.utcnow())
            data["message"]="%s" %(message)
            data["tags"]=tags
            data["exception"]=exc
            data["level"]=level
            data["logger"]=j.application.appname
            data["platform"]="python"
            data["server_name"]="g%s.n%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid)  
            data["extra"]=extra

            if tb<>None:
                from stacks import iter_traceback_frames,get_stack_info
                frames=iter_traceback_frames(tb)
                data.update({
                    'sentry.interfaces.Stacktrace': {
                        'frames': get_stack_info(frames)
                    },
                })
            else:
                data.update({
                    'sentry.interfaces.Stacktrace': {
                        'frames': backtrace
                    },
                })


            url2="%s/api/%s/store/"%(url,default)

            auth="Sentry sentry_version=5, sentry_timestamp=%s,"%j.base.time.getTimeEpoch()
            auth+="sentry_key=%s, sentry_client=raven-python/1.0,"%pub
            auth+="sentry_secret=%s"%secret

            headers = {'X-Sentry-Auth': auth}

            try:
                r = requests.post(url2,data=json.dumps(data), headers=headers, timeout=1)
            except Exception,e:  
                pass              
                # print "COULD NOT SEND \n%s \nTO SENTRY.\nReason:%s"%(data,e)
             
    def _dealWithRunningAction(self):
        """Function that deals with the error/resolution messages generated by j.action.start() and j.action.stop()
        such that when an action fails it throws a jumpscale event and is directed to be handled here
        """
        if j.__dict__.has_key("action") and j.action.hasRunningActions():
            j.console.echo("\n\n")
            j.action.printOutput()
            j.console.echo("\n\n")
            j.console.echo( "ERROR:\n%s\n" % j.action._runningActions[-1].errorMessage)
            j.console.echo( "RESOLUTION:\n%s\n" % j.action._runningActions[-1].resolutionMessage)
            j.action.clean()    

    def lastActionSet(self,lastActionDescription):
        """
        will remember action you are doing, this will be added to error message if filled in
        """
        self.lastAction=lastActionDescription

    def lastActionClear(self):
        """
        clear last action so is not printed when error
        """
        self.lastAction=""

    def escalateBugToDeveloper(self,errorConditionObject,tb=None):

        j.logger.enabled=False #no need to further log, there is error

        tracefile=""
        
        def findEditorLinux():
            apps=["sublime_text","geany","gedit","kate"]                
            for app in apps:
                try:
                    if j.system.unix.checkApplicationInstalled(app):
                        editor=app                    
                        return editor
                except:
                    pass
            return "less"

        if False and j.application.shellconfig.interactive:
            #if j.application.shellconfig.debug:
                #print "###ERROR: BACKTRACE"
                #print errorConditionObject.backtrace
                #print "###END: BACKTRACE"                

            editor = None
            if j.system.platformtype.isLinux():
                #j.console.echo("THIS ONLY WORKS WHEN GEDIT IS INSTALLED")
                editor = findEditorLinux()
            elif j.system.platformtype.isWindows():
                editorPath = j.system.fs.joinPaths(j.dirs.baseDir,"apps","wscite","scite.exe")
                if j.system.fs.exists(editorPath):
                    editor = editorPath
            tracefile=errorConditionObject.log2filesystem()
            #print "EDITOR FOUND:%s" % editor            
            if editor:
                #print errorConditionObject.errormessagepublic   
                if tb==None:
                    try:
                        res = j.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace)")
                    except:
                        #print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE EDITOR"
                        res="s"
                else:
                    try:
                        res = j.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace, d=debug)")
                    except:
                        #print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE EDITOR"
                        res="s"
                if res == "t":
                    cmd="%s '%s'" % (editor,tracefile)
                    #print "EDITORCMD: %s" %cmd
                    if editor=="less":
                        j.system.process.executeWithoutPipe(cmd,dieOnNonZeroExitCode=False)
                    else:
                        result,out=j.system.process.execute(cmd,dieOnNonZeroExitCode=False, outputToStdout=False)
                    
                j.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    j.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb; pdb.post_mortem(tb)
                elif res=="s":
                    #print errorConditionObject
                    j.application.stop(1)
            else:
                #print errorConditionObject
                res = j.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, d=debug)")
                j.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    j.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb; pdb.post_mortem()
                elif res=="s":
                    #print eobject
                    j.application.stop(1)

        else:
            #print "ERROR"
            #tracefile=eobject.log2filesystem()
            #print errorConditionObject
            #j.console.echo( "Tracefile in %s" % tracefile)
            j.application.stop(1)

    def halt(self,msg, eco=None):
        if eco is not None:
            eco = eco.__dict__
        raise HaltException(msg, eco)

import sys
import traceback
import string
import inspect

from JumpScale import j

from ErrorConditionObject import ErrorConditionObject


class ErrorConditionHandler():
    
    def __init__(self,haltOnError=True,storeErrorConditionsLocal=True):
        self.lastAction=""
        self.haltOnError=haltOnError     
        self.setExceptHook()
        self.lastEco=None
        self.sentryOwnClientInit=False
        
    def toolStripNonAsciFromText(text):
        return string.join([char for char in str(text) if ((ord(char)>31 and ord(char)<127) or ord(char)==10)],"")        
        
    def setExceptHook(self):
        sys.excepthook = self.excepthook
        self.inException=False
        
    def raiseBug(self, message,category="", pythonExceptionObject=None,pythonTraceBack=None,msgpub="",die=True,tags=""):
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
        if pythonExceptionObject<>None:
            eco=self.parsePythonErrorObject(pythonExceptionObject,level=1,message=message)            
            eco.category=category
        else:
            eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=1) 
            eco.getBacktrace()

        eco.tags=tags
        eco.type=j.enumerators.ErrorConditionType.BUG
        self.processErrorConditionObject(eco)
        if j.application.shellconfig.interactive:
         
            if pythonTraceBack<>None:
                return self.escalateBugToDeveloper(eco,pythonTraceBack)  
            elif pythonExceptionObject<>None:
                return self.escalateBugToDeveloper(eco)  
            else:
                eco.getBacktrace()
                return self.escalateBugToDeveloper(eco)   
        if die:                         
            self.halt()
        
    def raiseOperationalCritical(self, message="", category="",msgpub="",die=True,tags="",eco=None):
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
            eco.type=j.enumerators.ErrorConditionType.OPERATIONS
            eco.level=1

        self.processErrorConditionObject(eco,tostdout=False)

        eco.errormessage=eco.errormessage.strip("\"")

        msg = eco.errormessage 
        if j.application.config.get('system.debug', checkExists=True, defaultval='0') == '1':
            msg=str(eco)

        print "\n#########   Operational Critical Error    #################\n%s\n###########################################################\n"% msg
        print 
        if die:
            self.lastEco=eco
            if message=="":
                message=eco.errormessage
            raise RuntimeError(message)

    def raiseOperationalWarning(self, message="", category="",msgpub="",tags="",eco=None):
        if not eco:
            eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=2,\
                                         type=j.enumerators.ErrorConditionType.OPERATIONS)
            eco.tags=tags
        else:
            eco.type=j.enumerators.ErrorConditionType.OPERATIONS
            eco.level=1
        self.processErrorConditionObject(eco)
        
    def raiseInputError(self, message="", category="input",msgpub="",die=False ,backtrace="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=2,type=j.enumerators.ErrorConditionType.INPUT)
        eco.tags=tags
        if backtrace:
            eco.backtrace=backtrace
        self.processErrorConditionObject(eco)
        if die:
            self.halt()
        
    def raiseMonitoringError(self, message, category="",msgpub="",die=False,tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=2,type=j.enumerators.ErrorConditionType.MONITORING)
        eco.tags=tags
        self.processErrorConditionObject(eco)
        if die:
            self.halt()
        
    def raisePerformanceError(self, message, category="",msgpub="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=2,type=j.enumerators.ErrorConditionType.PERFORMANCE)
        eco.tags=tags
        self.processErrorConditionObject(eco)        
        
    def getErrorConditionObject(self,ddict={},msg="",msgpub="",category="",level=1,type=0):
        """
        @data is dict with fields of errorcondition obj
        returns only ErrorConditionObject which should be used in jumpscale to define an errorcondition (or potential error condition)
        
        """                
        errorconditionObject= ErrorConditionObject(ddict=ddict,msg=msg,msgpub=msgpub,level=level,category=category,type=type)                
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
        if tb==None:
            ttype, exc_value, tb=sys.exc_info()
        try:
            message2=pythonExceptionObject.message
            if message2.strip()=="":
                message2=str(pythonExceptionObject)
        except:
            message2=str(pythonExceptionObject)
            
        if message2.find("{category:")<>-1:
            cat=j.codetools.regex.findOne("\{ *category.*\:.*}",message2)
            cat=cat.split(":")[1].replace("}","").strip()
        else:
            cat=""
            
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
        
        try:
            backtrace = "~ ".join([res for res in traceback.format_exception(ttype, pythonExceptionObject, tb)])
            if len(backtrace)>10000:
                backtrace=backtrace[:10000]
        except:
            print "ERROR in trying to get backtrace"
        
        try:
            errorobject=self.getErrorConditionObject(msg=message,msgpub="",level=level)
            errorobject.category=cat
            errorobject.backtrace=backtrace
        except Exception,e:
            print "CRITICAL ERROR in trying to get errorobject, is BUG, please check (ErrorConditionHandler.py on line 202)"
            print "error:%s"%e
            sys.exit()

        errorobject.tb=tb
            
        try:
            errorobject.funcfilename=tb.tb_frame.f_code.co_filename
        except:
            pass
                        
        return errorobject        
    
    def parsepythonExceptionObject(self,*args,**kwargs):
        raise RuntimeError("Do not use .parsepythonExceptionObject method use .parsePythonErrorObject")

    def excepthook(self, ttype, pythonExceptionObject, tb):
        """ every fatal error in jumpscale or by python itself will result in an exception
        in this function the exception is caught.
        This routine will create an errorobject & escalate to the infoserver
        @ttype : is the description of the error
        @tb : can be a python data object or a Event
        """

        # print "jumpscale EXCEPTIONHOOK"
        
        if self.inException:
            print "ERROR IN EXCEPTION HANDLING ROUTINES, which causes recursive errorhandling behaviour."
            print pythonExceptionObject
            return 
            
        self.inException=True

               
        errorobject=self.parsePythonErrorObject(pythonExceptionObject,ttype=ttype,tb=tb)
        errorobject.tb=tb

        # if j.application.config.exists("sentry.server"):
        #         frames=self.getFrames(tb)
        #         frame=frames[-1][0]
        #             modulename=inspect.getmodulename(frame.f_code.co_filename)
        #         except:
        #             modulename="appname:%s"%(j.application.appname)
            
        #     self.sendMessageToSentry(modulename,errorConditionObject.errormessage,ttype="error",tags=None,extra=extra,level="error",tb=tb)
        #     # client=self.getSentryClient()
        #     # client.captureException(
        #     # exc_info=(ttype, pythonExceptionObject, tb),
        #     # extra={
        #     #     'gid': j.application.whoAmI.gid,
        #     #     'nid': j.application.whoAmI.nid,
        #     #     'appname':j.application.appname,
        #     #     #'tb':errorobject.backtrace,
        #     #     })


        if self.lastAction<>"":
            j.logger.log("Last action done before error was %s" % self.lastAction)
        
        self._dealWithRunningAction()      
                
        self.inException=False             
        
        self.processErrorConditionObject(errorobject,sentry=True)

        if j.application.shellconfig.interactive:
            return self.escalateBugToDeveloper(errorobject,tb)

    def checkErrorIgnore(self,eco):
        ignorelist=["KeyboardInterrupt"]
        for item in ignorelist:
            if eco.errormessage.find(item)<>-1:
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
        else:
            frames=[]
            while tb: #copied from sentry raven lib (BSD license)
                # support for __traceback_hide__ which is used by a few libraries
                # to hide internal frames.
                f_locals = getattr(tb.tb_frame, 'f_locals', {})
                if not _getitem_from_frame(f_locals, '__traceback_hide__'):
                    frames.append((tb.tb_frame, getattr(tb, 'tb_lineno', None)))
                tb = tb.tb_next
        
        result=[]
        ignore=["ipython","errorconditionhandler"]
        for frame,linenr in frames:
            name=frame.f_code.co_filename
            toignore=False
            for check in ignore:
                if name.find(check)<>-1:
                    toignore=True
            if not toignore:
                result.append((frame,linenr))
        return result

    def processErrorConditionObject(self,errorConditionObject,tostdout=True,sentry=True,modulename=None):
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

        errorConditionObject.toAscii()

        if self.checkErrorIgnore(errorConditionObject):
            return

        if j.logger.logTargetLogForwarder and j.logger.logTargetLogForwarder.enabled:
            j.logger.logTargetLogForwarder.logECO(errorConditionObject)

        if tostdout:
            print errorConditionObject

        if sentry and j.application.config.exists("sentry.server"):
            extra={}
            tb=errorConditionObject.tb
            
            extra["tb"]=errorConditionObject.backtrace
            extra["category"]=errorConditionObject.category
            
            self.sendMessageToSentry(modulename=modulename,message=errorConditionObject.errormessage,ttype="error",tags=None,extra=extra,level="error",tb=tb)
            # client=self.getSentryClient()            
            # print client.capture('raven.events.Message', message=errorConditionObject.errormessage,extra={
            #     'gid': j.application.whoAmI.gid,
            #     'nid': j.application.whoAmI.nid,
            #     'appname':j.application.appname,
            #     'tb':errorConditionObject.backtrace,
            #     'category':errorConditionObject.category,
            #     'appname':errorConditionObject.appname
            #     })
            

        return errorConditionObject

    def getSentryClient(self):
        if j.application.config.exists("sentry.server"):
            server=j.application.config.get("sentry.server")
            pub=j.application.config.get("sentry.public.key")
            secret=j.application.config.get("sentry.secret.key")
            port=int(j.application.config.get("sentry.port"))
            default=j.application.config.get("sentry.project.default")
            from raven import Client
            url='http://%s:%s@%s:%s/%s'%(pub,secret,server,port,default)
            client = Client(url)
            client.name="g%s.n%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid)            
            return client
        raise RuntimeError("sentry client should not be asked when not enabled")

    def sendMessageToSentry(self,modulename,message,ttype="bug",tags=None,extra={},level="error",tb=None):
        """
        @param level        
            fatal
            error
            warning
            info
            debug

        """

        if j.application.config.exists("sentry.server"):
            import requests
            import ujson
            import uuid
            import datetime
            server=j.application.config.get("sentry.server")
            pub=j.application.config.get("sentry.public.key")
            secret=j.application.config.get("sentry.secret.key")
            port=int(j.application.config.get("sentry.port"))
            default=j.application.config.get("sentry.project.default")
            url='http://%s:%s/'%(server,port)
            exc={}
            exc["type"]=ttype
            exc["value"]=message

            if modulename==None:
                try:
                    frames=self.getFrames(tb)
                    frame=frames[-1][0]
                    
                    modulename=inspect.getmodulename(frame.f_code.co_filename)
                    modulename=str(inspect.getmodule(frame)).replace("<module ","").replace("'","").replace(".pyc","").replace(">","")
                    try:
                        modulename=modulename.split("from")[0].strip()
                    except:
                        pass
                except:
                    modulename="appname:%s"%(j.application.appname)                
                
            exc["module"]=modulename
            exc=[exc]
            if tags==None:
                tags={}
            else:
                tags=j.core.tags.getObject(tags)
                tags=tags.getDict()
                
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


            url2="%s/api/%s/store/"%(url,default)

            auth="Sentry sentry_version=5, sentry_timestamp=%s,"%j.base.time.getTimeEpoch()
            auth+="sentry_key=%s, sentry_client=raven-python/1.0,"%pub
            auth+="sentry_secret=%s"%secret

            headers = {'X-Sentry-Auth': auth}

            try:
                r = requests.post(url2,data=ujson.dumps(data), headers=headers, timeout=1)
            except Exception,e:                
                print "COULD NOT SEND \n%s \nTO SENTRY.\nReason:%s"%(data,e)
            

    
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

    def halt(self):
        j.application.stop(1)

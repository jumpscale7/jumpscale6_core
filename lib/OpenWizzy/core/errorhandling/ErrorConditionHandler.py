import sys
import traceback
import string

from OpenWizzy import o

from ErrorConditionObject import ErrorConditionObject


class ErrorConditionHandler():
    
    def __init__(self,haltOnError=True,storeErrorConditionsLocal=True):
        self.lastAction=""
        self.haltOnError=haltOnError     
        self.setExceptHook()
        
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
            o.errorconditionhandler.raiseBug("an error",category="exceptions.init",e)
        
        """
        if pythonExceptionObject<>None:
            eco=self.parsePythonErrorObject(pythonExceptionObject,level=1,message=message)            
            eco.category=category
        else:
            eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=1) 
            eco.getBacktrace()
                                  
        eco.tags=tags
        eco.type=type=o.enumerators.ErrorConditionType.BUG
        self.processErrorConditionObject(eco)
        if o.application.shellconfig.interactive:
         
            if pythonTraceBack<>None:
                return self.escalateBugToDeveloper(eco,pythonTraceBack)  
            elif pythonExceptionObject<>None:
                return self.escalateBugToDeveloper(eco)  
            else:
                eco.getBacktrace()
                return self.escalateBugToDeveloper(eco)   
        if die:                         
            self.halt()

        
    def raiseOperationalCritical(self, message, category="",msgpub="",die=True,tags=""):
        """
        use this to raise an operational issue about the system
        @param message is message we want to use for operators
        @param msgpub is message we want to show to endcustomers (can include a solution)
        @param category is a dot notation to give category for the error condition
        """
        
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=1,\
                                         type=o.enumerators.ErrorConditionType.OPERATIONS)
        eco.tags=tags
        self.processErrorConditionObject(eco)    
        if die:
            self.halt()        
    
    def raiseOperationalWarning(self, message="", category="",msgpub="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,level=2,\
                                         type=o.enumerators.ErrorConditionType.OPERATIONS)
        eco.tags=tags
        self.processErrorConditionObject(eco)
        
    def raiseInputError(self, message="", category="input",msgpub="",die=False ,backtrace="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=2,type=o.enumerators.ErrorConditionType.INPUT)
        eco.tags=tags
        if backtrace<>"":
            errorConditionObject.backtrace=backtrace        
        self.processErrorConditionObject(eco)
        if die:
            self.halt()
        
    def raiseMonitoringError(self, message, category="",msgpub="",die=False,tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=2,type=o.enumerators.ErrorConditionType.MONITORING)
        eco.tags=tags
        self.processErrorConditionObject(eco)
        if die:
            self.halt()
        

    def raisePerformanceError(self, message, category="",msgpub="",tags=""):
        eco=self.getErrorConditionObject(msg=message,msgpub=msgpub,category=category,\
                                         level=2,type=o.enumerators.ErrorConditionType.PERFORMANCE)
        eco.tags=tags
        self.processErrorConditionObject(eco)        
        
    def getErrorConditionObject(self,ddict={},msg="",msgpub="",category="",level=1,type=0):
        """
        @data is dict with fields of errorcondition obj
        returns only ErrorConditionObject which should be used in openwizzy 6 to define an errorcondition (or potential error condition)
        
        """                
        errorconditionObject= ErrorConditionObject(ddict=ddict,msg=msg,msgpub=msgpub,level=level,category=category,type=type)                
        return errorconditionObject        
  
    def processPythonExceptionObject(self,pythonExceptionObject,ttype=None, tb=None,level=1,message=""):
        """ 
        how to use
        
        try:
            ##do something            
        except Exception,e:
            o.errorconditionhandler.processpythonExceptionObject(e)
            
        @param pythonExceptionObject is errorobject thrown by python when there is an exception
        @param ttype : is the description of the error, can be None
        @param tb : can be a python data object for traceback, can be None
        
        @return [ecsource,ecid,ecguid]
        
        the errorcondition is then also processed e.g. send to local logserver and/or stored locally in errordb
        see o.errorconditionhandler.processErrorConditionObject how to use this and overrule the behaviour
        """        
        obj=self.parsePythonErrorObject(pythonExceptionObject,ttype, tb,level,message)

        return self.processErrorConditionObject(obj)
        
        

    def parsePythonErrorObject(self,pythonExceptionObject,ttype=None, tb=None,level=1,message=""):
        
        """ 
        how to use
        
        try:
            ##do something            
        except Exception,e:
            eco=o.errorconditionhandler.parsePythonErrorObject(e)

        eco is openwizzy internal format for an error 
        next step could be to process the error objecect (eco) e.g. by o.errorconditionhandler.processErrorConditionObject(eco)
            
        @param pythonExceptionObject is errorobject thrown by python when there is an exception
        @param ttype : is the description of the error, can be None
        @param tb : can be a python data object for traceback, can be None
        
        @return a ErrorConditionObject object as used by openwizzy6 (should be the only type of object we send around)
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
            cat=o.codetools.regex.findOne("\{ *category.*\:.*}",message2)
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
            print "CRITICAL ERROR in trying to get errorobject, is BUG, please check (ErrorConditionHandler.py on line 196)"
            print "error:%s"%e
            sys.exit()
            
        try:
            errorobject.funcfilename=tb.tb_frame.f_code.co_filename
        except:
            pass
                        
        return errorobject        
    
    def parsepythonExceptionObject(self,*args,**kwargs):
        raise RuntimeError("Do not use .parsepythonExceptionObject method use .parsePythonErrorObject")

    def excepthook(self, ttype, pythonExceptionObject, tb):
        """ every fatal error in openwizzy or by python itself will result in an exception
        in this function the exception is caught.
        This routine will create an errorobject & escalate to the infoserver
        @ttype : is the description of the error
        @tb : can be a python data object or a Event
        """
        
        #print "openwizzy6 EXCEPTIONHOOK"
        
        if self.inException:
            print "ERROR IN EXCEPTION HANDLING ROUTINES, which causes recursive errorhandling behaviour."
            print errorObject
            return 
            
        self.inException=True
           
        errorobject=self.parsePythonErrorObject(pythonExceptionObject,ttype=ttype,tb=tb)
        
        
        if self.lastAction<>"":
            o.logger.log("Last action done before error was %s" % self.lastAction)
            message="%s\n%s\n" % (message,"Last action done before error was: %s" % self.lastAction)
        
        self._dealWithRunningAction()      
                
        self.inException=False             
        
        self.processErrorConditionObject(errorobject)

        if o.application.shellconfig.interactive:
            #@todo kristof: get more detailed stacktrace
            return self.escalateBugToDeveloper(errorobject,tb)

    def checkErrorIgnore(self,eco):
        ignorelist=["KeyboardInterrupt"]
        for item in ignorelist:
            if eco.errormessage.find(item)<>-1:
                return True
        return False

        
    def processErrorConditionObject(self,errorConditionObject):
        """
        a errorObject gets processed which means stored locally or forwarded to a logserver or both
        @return [ecsource,ecid,ecguid]

        you can overrule this behaviour by changing at rutime this function with a new one e.g. following code could work

        ### code:
        def myProcessErrorConditionObject(eco):
            print eco

        o.errorconditionhandler.processErrorConditionObject=myProcessErrorConditionObject
        ###

        now there would be no further processing appart from priting the errorcondition object (eco)

        """

        if self.checkErrorIgnore(errorConditionObject):
            return

        print errorConditionObject

        if o.logger.clientdaemontarget<>False:
            try:
                o.logger.clientdaemontarget.loggerClient.logECO(errorConditionObject)
            except Exception,e:
                from OpenWizzy.core.Shell import ipshellDebug,ipshell
                print "DEBUG NOW error in error escalation in openwizzy main log target for loggerclient"
                ipshell()

        return errorConditionObject
        
    
    def _dealWithRunningAction(self):
        """Function that deals with the error/resolution messages generated by o.action.start() and o.action.stop()
        such that when an action fails it throws a openwizzy event and is directed to be handled here
        """
        if o.__dict__.has_key("action") and o.action.hasRunningActions():
            o.console.echo("\n\n")
            o.action.printOutput()
            o.console.echo("\n\n")
            o.console.echo( "ERROR:\n%s\n" % o.action._runningActions[-1].errorMessage)
            o.console.echo( "RESOLUTION:\n%s\n" % o.action._runningActions[-1].resolutionMessage)
            o.action.clean()    

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

        o.logger.enabled=False #no need to further log, there is error

        tracefile=""
        
        def findEditorLinux():
            apps=["geany","gedit","kate"]                
            for app in apps:
                try:
                    if o.system.unix.checkApplicationInstalled(app):
                        editor=app                    
                        return editor
                except:
                    pass
            return "less"        

        if o.application.shellconfig.interactive:
            #if o.application.shellconfig.debug:
                #print "###ERROR: BACKTRACE"
                #print errorConditionObject.backtrace
                #print "###END: BACKTRACE"                

            editor = None
            if o.system.platformtype.isLinux():
                #o.console.echo("THIS ONLY WORKS WHEN GEDIT IS INSTALLED")
                editor = findEditorLinux()
            elif o.system.platformtype.isWindows():
                editorPath = o.system.fs.joinPaths(o.dirs.baseDir,"apps","wscite","scite.exe")
                if o.system.fs.exists(editorPath):
                    editor = editorPath
            tracefile=errorConditionObject.log2filesystem()
            #print "EDITOR FOUND:%s" % editor            
            if editor:
                #print errorConditionObject.errormessagepublic   
                if tb==None:
                    try:
                        res = o.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace)")
                    except:
                        #print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE EDITOR"
                        res="s"
                else:
                    try:
                        res = o.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace, d=debug)")
                    except:
                        #print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE EDITOR"
                        res="s"
                if res == "t":
                    cmd="%s '%s'" % (editor,tracefile)
                    #print "EDITORCMD: %s" %cmd
                    if editor=="less":
                        o.system.process.executeWithoutPipe(cmd,dieOnNonZeroExitCode=False)
                    else:
                        result,out=o.system.process.execute(cmd,dieOnNonZeroExitCode=False, outputToStdout=False)
                    
                o.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    o.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb; pdb.post_mortem(tb)
                elif res=="s":
                    #print errorConditionObject
                    o.application.stop(1)
            else:
                #print errorConditionObject
                res = o.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, d=debug)")
                o.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    o.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb; pdb.post_mortem()
                elif res=="s":
                    #print eobject
                    o.application.stop(1)

        else:
            #print "ERROR"
            #tracefile=eobject.log2filesystem()
            #print errorConditionObject
            #o.console.echo( "Tracefile in %s" % tracefile)
            o.application.stop(1)

    def halt(self):
            o.application.stop(1)

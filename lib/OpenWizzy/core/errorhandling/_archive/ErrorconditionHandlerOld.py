import traceback
import sys
from OpenWizzy import o

from OpenWizzy.core.messages.ErrorconditionObject import ErrorconditionObject
from OpenWizzy.core.messages.ErrorConditionType import ErrorConditionTypeFactory

class ErrorconditionHandler():
    '''
    The EventHandler class catches errors, messages or warnings and
    processes them
    '''
    def __init__(self):
        sys.excepthook = self._exceptionhook
        self._sep="*-***********************-*" #separater used in encoding/decoding to messages
        self.lastErrorconditionObject=None
        self.lastCriticalErrorconditionObject=None
        self.lastErrConTimes = dict()
        self.lastErrConMessages = dict()
        self.lastErrConTags = dict()

        self.lastAction=""

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

    def _raise(self, message, messageprivate='', level=None, typeid='', tags=''):
        """
        @param message: is public message which can be shown to end users
        @type message: string
        @param messageprivate: is private error message which will not be shows to end users
        @type messageprivate: string
        @param level: the ErrorconditionLevel
        @type level: int
        @param typeid: Event type identifier
        @type typeid: string
        @param tags: (see o.tags... to construct a tagstring)
        @type tags: string
        """
        ###SSOBF 4967 - escalate all events = based on evt_type_def it might be forwarded to noc
    
        message=o.system.string.toolStripNonAsciFromText(message)
        messageprivate=o.system.string.toolStripNonAsciFromText(messageprivate)
        #we need simlink between /opt/qbase3/cfg/evt_type_def and /opt/qbase6/cfg/evt_type_def
        
        errConType = ErrorConditionTypeFactory.getType(typeid)
        
        solution = ""
        if errConType is not None:
            solution = errConType.definition.solution
            if len(solution) > 0 :
                messageprivate = "%sPossible solution:\n%s" % ('%s\n'%messageprivate if messageprivate else '', solution)

        # Build params for the error condition type
        try :
            errConObj = ErrorconditionObject()                 
            errConObj.init(message, messageprivate, level, typeid, tags, None) #no backtrace?
            source= o.application.agentid+"_"+o.application.appname
        
            params = dict()
            params[ "messageobject"] = errConObj
            params[ "source" ] = source
            
            errConType = ErrorConditionTypeFactory.getType ( errConObj.typeid )
            if errConType is not None :
                params.update( errConType.getEscalationParamDict() )
                if len ( params ) != 0 :
                    params[ "lastErrorConditionTimestamps" ] = self.lastErrConTimes
                    params[ "lastErrorConditionMessages" ] = self.lastErrConMessages
                    params[ "lastErrorConditionTags" ] = self.lastErrConTags
            
            if len(params) > 0 :
                o.messagehandler.sendMessage(errConObj, params)
                
        except Exception, ex:
            o.logger.log( "Error condition escalation failed. (%s: '%s')" % (ex.__class__.__name__, ex) , 1)

        
        ###############
        eobject=ErrorconditionObject()

        eobject.init(message=message, messageprivate=messageprivate, level=level, typeid=typeid, tags=tags)        

        if eobject.level ==o.enumerators.ErrorconditionLevel.CRITICAL:
            self._raiseCriticalErrorObject(eobject)
        else:
            self._raiseAnyErrorObject(eobject)

        if int(eobject.level) <= 3:
            raise Exception(eobject.errormessagepublic)
        else:
            o.logger.log(eobject.errormessagepublic, 3)

    def raiseCritical(self, message, messageprivate="", typeid="", tags=""):
        self._raise(message, messageprivate, o.enumerators.ErrorconditionLevel.CRITICAL, typeid, tags)
    
    def raiseError(self, message, messageprivate="", typeid="", tags=""):
        self._raise(message, messageprivate, o.enumerators.ErrorconditionLevel.ERROR, typeid, tags)

    def raiseWarning(self, message, messageprivate="", typeid="", tags=""):
        self._raise(message, messageprivate, o.enumerators.ErrorconditionLevel.WARNING, typeid, tags)

    def raiseInfo(self, message, messageprivate="", typeid="", tags=""):
        self._raise(message, messageprivate, o.enumerators.ErrorconditionLevel.INFO, typeid, tags)


    def escalateEvent(self, message='', messageprivate='', level=None, typeid='', tags='', backtrace=None):
        """
        escalation now done by tasklets directory 'eventmanagement
        """
        raise NotImplementedError("Do not use, just raise the error escalation will happen")

    def _exceptionhook(self, ttype, errorObject, tb, stop=True):
        """ every fatal error in openwizzy or by python itself will result in an exception
        in this function the exception is caught.
        @ttype : is the description of the error
        @tb : can be a python data object or a Event
        """
        try:
            message=errorObject.message
            if message.strip()=="":
                message=str(errorObject)
        except:
            message=str(errorObject)
        try:
            type_str=str(ttype).split("exceptions.")[1].split("'")[0]
        except:
            type_str=str(ttype)
            
        if type_str.lower().find("exception")==-1:
            message="%s: %s" % (type_str,message)
        
        if self.lastAction<>"":
            o.logger.log("Last action done before error was %s" % self.lastAction)
            message="%s\n%s\n" % (message,"Last action done before error was: %s" % self.lastAction)

        self._dealWithRunningAction()

        backtrace = "~ ".join([res for res in traceback.format_exception(ttype, errorObject, tb)])

        if self.lastCriticalErrorconditionObject<>None:            
            eobject=self.lastCriticalErrorconditionObject
            self.lastCriticalErrorconditionObject=None
            eobject.backtrace=backtrace
        else:
            #if isinstance(errorObject, Exception):
            backtrace = "~ ".join([res for res in traceback.format_exception(ttype, errorObject, tb)])
    
            eobject=ErrorconditionObject()
    
            eobject.init(message=message, messageprivate='', level=o.enumerators.ErrorconditionLevel.CRITICAL, typeid='', tags='', tb=tb,backtracebasic=backtrace)        
            
        self._raiseCriticalErrorObject(eobject)
        

    def _raiseAnyErrorObject(self,eobject):
        """
        call tasklets in dir 'eventmanagement' relative to app launched
        tasklets will be called with params.errorobject as parameter
        tasklets can do escalation
        """
        if o.system.fs.exists("eventmanagement"):
            te=o.core.taskletengine.get("eventmanagement")
            params=o.core.params.get()
            params.errorobject=eobject
            te.execute(params)
        #print "INTERACTIVE:%s"%o.application.shellconfig.interactive        

    def _raiseCriticalErrorObject(self, eobject):
        """
        raise critical error to screen & if needed launch editor with more info like stacktrace
        also escalates to tasklets in dir called 'eventmanagement' see applicationserver2 default app in openwizzycore
        """
        self.lastErrorconditionObject=eobject
        
        self._raiseAnyErrorObject(eobject)
        
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
            o.logger.log(eobject)
            if o.application.shellconfig.debug:
                print "###ERROR: BACKTRACE"
                print eobject.backtrace
                print "###END: BACKTRACE"                

            editor = None
            if o.system.platformtype.isLinux():
                #o.console.echo("THIS ONLY WORKS WHEN GEDIT IS INSTALLED")
                editor = findEditorLinux()
            elif o.system.platformtype.isWindows():
                editorPath = o.system.fs.joinPaths(o.dirs.baseDir,"apps","wscite","scite.exe")
                if o.system.fs.exists(editorPath):
                    editor = editorPath
            tracefile=eobject.log2filesystem()
            #print "EDITOR FOUND:%s" % editor            
            if editor:
                print eobject.errormessagepublic                
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
                    import pdb; pdb.post_mortem()
                elif res=="s":
                    print eobject
                    o.application.stop(1)
            else:
                print eobject
                res = o.console.askString("\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, d=debug)")
                o.logger.clear()
                if res == "c":
                    return
                elif res == "d":
                    o.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb; pdb.post_mortem()
                elif res=="s":
                    print eobject
                    o.application.stop(1)

        else:
            print "ERROR"
            tracefile=eobject.log2filesystem()
            print eobject
            o.console.echo( "Tracefile in %s" % tracefile)
            o.application.stop(1)
            

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

    def getCurrentExceptionString(self, header = None):
        """ Get description on exception currently being handled """
        if (header == None or header == ""):
            result = ""
        else:
            result = header + "\n"

        e1, e2, e3 = sys.exc_info()
        for x in traceback.format_exception(e1, e2, e3):
            result = result + x

        return result

import copy

from OpenWizzy import o
import traceback

# class Base():
    
#     def __str__(self):
#         return str(self.object2dict())
            
#     __repr__=__str__
    
#     def obj2dict(self):
#         data={}
#         def todict(obj,data):
#             for key, value in obj.__dict__.iteritems():
#                 try:
#                     data[key] = todict(value,data)
#                 except AttributeError:
#                     data[key] = value
#             return data   
#         return todict(self,data)    

class AlertObject():
    def __init__(self):
        self.id=0  #is unique where alert has been created
        self.guid=o.base.idgenerator.generateGUID() #can be used for authentication purposes
        self.description=""
        self.descriptionpub=""
        self.level=1 #1:critical, 2:warning, 3:info
        self.errorconditions=[]
        self.category="" #dot notation e.g. machine.start.failed
        self.tags="" #e.g. machine:2323
        self.state="NEW" #["NEW","ALERT","CLOSED"]
        seld.inittime=0 #first time there was an error condition linked to this alert
        self.lasttime=0 #last time there was an error condition linked to this alert
        self.closetime=0  #alert is closed, no longer active
        self.nrerrorconditions=1 #nr of times this error condition happened
        self.transactionsinfo="" 
        
    def getLastECO(self):
        pass #@todo
        

class ErrorConditionObject():
    """
    used enumerators:
    - o.enumerators.ErrorConditionLevel.
    - o.enumerators.ErrorConditionType.
    """
    def __init__(self,ddict={},msg="",msgpub="",category="",level=1,type=0):
        if ddict<>{}:
            self.__dict__=ddict
        else:
            self.guid=o.base.idgenerator.generateGUID()
            self.category=category #is category in dot notation
            self.errormessage=msg
            self.errormessagePub=msgpub
            self.level=int(level) #1:critical, 2:warning, 3:info see o.enumerators.ErrorConditionLevel.

            self.code=""
            self.funcname=""
            self.funcfilename=""
            self.funclinenr=0
            self.backtrace=""

            self.appname=o.application.appname #name as used by application
            
            if hasattr(o.application, 'whoAmI'):
                if len(o.application.whoAmI)==3:
                    self.gid = o.application.whoAmI[0]
                    self.nid = o.application.whoAmI[1]
                    self.bid = 0
                    self.aid = 0
                    self.pid = 0
                    self.jid = 0
                    self.masterjid = 0
                elif len(o.application.whoAmI)==4:
                    self.gid = o.application.whoAmI[0]
                    self.bid = o.application.whoAmI[1]
                    self.nid = o.application.whoAmI[2]
                    self.pid = o.application.whoAmI[3]
                    self.aid = o.core.grid.aid
                    self.jid = 0
                    self.masterjid = 0
                else:
                    o.errorconditionhandler.raiseBug(message="whoAmi should be 3 or 4 items",category="log.id")
            else:    
                self.jid=0
                self.masterjid = 0
                self.gid=0
                self.bid=0
                self.nid=0
                self.pid=0
                self.aid=0

            self.epoch= o.base.time.getTimeEpoch()
            self.tags=""
            self.type=int(type) #o.enumerators.ErrorConditionType

    def __str__(self):
        if o.basetype.integer.check(self.type):
            ttype=str(o.enumerators.ErrorConditionType.getByLevel(int(self.type)))
        else:
            ttype=str(self.type)
        level=str(o.enumerators.ErrorConditionLevel.getByLevel(int(self.level)))
        content="\n\n***ERROR***\n"
        if self.backtrace<>"":
            content="%s\n" % self.backtrace
        content+="type/level: %s/%s\n" % (ttype,level)
        content+="%s\n" % self.errormessage
        if self.errormessagePub<>"":
            content+="errorpub: %s\n" % self.errormessagePub
        return content
            
    __repr__=__str__
    
    def log2filesystem(self):
        """
        write errorcondition to filesystem
        """
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.logDir,"errors",o.application.appname))
        path=o.system.fs.joinPaths(o.dirs.logDir,"errors",o.application.appname,"backtrace_%s.log"%(o.base.time.getLocalTimeHRForFilesystem()))        
        msg="***ERROR BACKTRACE***\n"
        msg+="%s\n"%self.backtrace
        msg+="***ERROR MESSAGE***\n"
        msg+="%s\n"%self.errormessage
        if self.errormessagePub<>"":
            msg+="%s\n"%self.errormessagePub
        if len(o.logger.logs)>0:
            msg+="\n***LOG MESSAGES***\n"
            for log in o.logger.logs:
                msg+="%s\n"%log
                
        msg+="***END***\n"
        
        o.system.fs.writeFile(path,msg)
        return path    
    
    def getBacktrace(self):
        stack=""
        if o.application.skipTraceback:
            return stack
        for x in traceback.format_stack():
            ignore=False            
            #if x.find("IPython")<>-1 or x.find("MessageHandler")<>-1 \
            #   or x.find("EventHandler")<>-1 or x.find("ErrorconditionObject")<>-1 \
            #   or x.find("traceback.format")<>-1 or x.find("ipython console")<>-1:
            #    ignore=True
            stack = "%s"%(stack+x if not ignore else stack)
            if len(stack)>50:
                self.backtrace=stack
                return 
        self.backtrace=stack
        
    def _filterLocals(self,k,v):
        try:
            k="%s"%k
            v="%s"%v
            if k in ["re","q","openwizzy","pprint","qexec","qshell","Shell","__doc__","__file__","__name__","__package__","i","main","page"]:
                return False
            if v.find("<module")<>-1:
                return False
            if v.find("IPython")<>-1:
                return False
            if v.find("<built-in function")<>-1:
                return False
            if v.find("openwizzy.Shell")<>-1:
                return False
        except:
            return False

        return True

    def getBacktraceDetailed(self,tracebackObject=""):
        """
        Get stackframe log
        is a very detailed log with filepaths, code locations & global vars, this output can become quite big
        """        
        if o.application.skipTraceback:
            return ""
        sep="\n"+"-"*90+"\n"
        result = ''
        if not tracebackObject:
            return "" #@todo needs to be fixed so it does work
        if tracebackObject==None:
            tracebackObject = inspect.currentframe()  #@todo does not work
        frames = inspect.getinnerframes(tracebackObject, 16)
        nrlines=0
        for (frame, filename, lineno, fun, context, idx) in frames:
            ##result = result + "-"*50 + "\n\n"
            nrlines+=1
            if nrlines>100:
                return result
            location=filename + "(line %d) (function %s)\n" % (lineno, fun)
            if location.find("EventHandler.py")==-1:
                result += "  " + sep
                result += "  " + location
                result += "  " + "========== STACKFRAME==========\n"
                if context:
                    l = 0
                    for line in context:
                        prefix = "    "
                        if l == idx:
                            prefix = "--> "
                        l += 1
                        result += prefix + line
                        nrlines+=1
                        if nrlines>100:
                            return result
                result += "  " + "============ LOCALS============\n"
                for (k,v) in sorted(frame.f_locals.iteritems()):
                    if self._filterLocals(k,v):
                        try:
                            result += "    %s : %s\n" % (str(k), str(v))
                        except:
                            pass
                        nrlines+=1
                        if nrlines>100:
                            return result

                        ##result += "  " + "============ GLOBALS============\n"
                ##for (k,v) in sorted(frame.f_globals.iteritems()):
                ##    if self._filterLocals(k,v):
                ##        result += "    %s : %s\n" % (str(k), str(v))
        self.backtrace=result


    def getCategory(self):
        return "eco"

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid=int(self.gid)
        self.bid=int(self.bid)
        self.id=int(self.id)
        return self.guid

    def getObjectType(self):
        return 3

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [3,1,self.guid,self.__dict__]

    def getContentKey(self):
        """
        return unique key for object, is used to define unique id
        
        """
        dd=copy.copy(self.__dict__)
        if dd.has_key("_ckey"):
            dd.pop("_ckey")
        if dd.has_key("id"):
            dd.pop("id")
        if dd.has_key("guid"):
            dd.pop("guid")
        if dd.has_key("sguid"):
            dd.pop("sguid")
        return o.tools.hash.md5_string(str(dd))
        
    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.getContentKey()

    
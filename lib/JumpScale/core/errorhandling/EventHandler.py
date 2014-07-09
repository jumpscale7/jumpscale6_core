from JumpScale import j

class EventHandler(object):

    def bug_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:B))"%category
        j.errorconditionhandler.raiseCritical(msg,category=category, pythonExceptionObject=e,die=False)

    def bug_warning(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:W))"%category
        j.errorconditionhandler.raiseWarning(msg,category=category, pythonExceptionObject=e)

    def opserror_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """    
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:O))"%category
        j.errorconditionhandler.raiseOperationalCritical(msg, category=category)

    def opserror(self,msg,category="",e=None):
        """
        will NOT die
        will make warning event is the same as opserror_warning
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        j.errorconditionhandler.raiseOperationalWarning(msg,category=category)

    opserror_warning = opserror


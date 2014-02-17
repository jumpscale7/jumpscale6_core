from JumpScale import j

class EventHandler():
    
    def bug_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR THROWN:%s\n"%e
        msg+="((C:%s L:1 T:B))"%category
        raise RuntimeError(msg)

    def opserror_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """    
        if e<>None:
            msg+="\nERROR THROWN:%s\n"%e
        msg+="((C:%s L:1 T:O))"%category
        raise RuntimeError(msg)

    def opserror(self,msg,category="",e=None):
        """
        will NOT die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR THROWN:%s\n"%e
        j.errorconditionhandler.raiseOperationalCritical(msg,category=category,die=False)

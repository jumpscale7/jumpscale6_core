from JumpScale import j

class EventHandler(object):

    def __init__(self):
        self.__aclient = None

    def bug_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:B))"%category
        raise RuntimeError(msg)

    def bug_warning(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:B))"%category
        j.errorconditionhandler.raiseBug(msg,category=category, pythonExceptionObject=e,die=False)

    def opserror_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """    
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:O))"%category
        raise RuntimeError(msg)

    def opserror(self,msg,category="",e=None):
        """
        will NOT die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        j.errorconditionhandler.raiseOperationalCritical(msg,category=category,die=False)

from JumpScale import j

class RaiseHandler():
    
    def bug_critical(self,msg,category=""):
        """
        will die
        """        
        msg+="((C:%s L:1 T:B))"%category
        raise RuntimeError(msg)

    def opserror_critical(self,msg,category=""):
        """
        will die
        """        
        msg+="((C:%s L:1 T:O))"%category
        raise RuntimeError(msg)

    def opserror(self,msg,category=""):
        """
        will NOT die
        """        
        from IPython import embed
        print "DEBUG NOW opserror"
        embed()
        
from JumpScale import j
import JumpScale.baselib.redis

from CmdRouter import CmdRouter

class CmdRouterFactory:

    """
    """
    def get(self,path):
        return CmdRouter(path)
        
        

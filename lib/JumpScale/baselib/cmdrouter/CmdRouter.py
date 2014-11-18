from JumpScale import j

import JumpScale.baselib.redis
import JumpScale.grid.jumpscripts


class CmdRouter(object):
    def __init__(self,  path=None):
        j.core.jumpscripts.load(path)
       
    def route(self,organization,actor,name,**args):
        pass

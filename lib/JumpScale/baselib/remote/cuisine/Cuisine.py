from JumpScale import j

import JumpScale.baselib.remote.fabric

j.system.platform.ubuntu.check()

import cuisine


class Cuisine():

    def __init__(self):
        self.api = cuisine
        self.fabric = j.remote.fabric.api
        j.remote.fabric.setHost()

    def help(self):
        C = """
import JumpScale.baselib.remote.cuisine        
#easiest way to use do:
c=j.remote.cuisine
#and then

c.user_ensure(...)
        """
        print C

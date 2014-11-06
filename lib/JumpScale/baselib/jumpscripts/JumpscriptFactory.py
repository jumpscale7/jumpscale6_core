from JumpScale import j
import time
import imp
import linecache
import inspect
import JumpScale.baselib.redis
import multiprocessing
from Jumpscript import Jumpscript

class JumpscriptFactory:

    """
    """
    def __init__(self):
        self.jumpscripts={}
        j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.tmpDir,"jumpscripts"))

    def getJSClass(self):
        return Jumpscript

    def load(self,path):
        for item in j.system.fs.listFilesInDir(path,True,filter="*.py"):
            basename=j.system.fs.getBaseName(item)
            if basename[0]=="_":
                continue
            basename=basename.replace(".py","")
            actor,name=basename.split("__",1)
            js=Jumpscript(path=item,name=name,actor=actor)
            key="%s_%s_%s"%(js.organization,js.actor,js.name)
            self.jumpscripts[key]=js

    def execute(self,organization,actor,name,**args):
        from IPython import embed
        print "DEBUG NOW id"
        embed()
            


        
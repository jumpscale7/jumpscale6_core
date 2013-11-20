from JumpScale import j
import imp

from types import MethodType

class ActionManager:
    """
    the action manager is responsible for executing the actions linked to a jpackages
    """

    def __init__(self,jp):
        # print "init actions for %s"%jp
        self._jpackage=jp
        self._actions={}
        self._done={}

        for path in j.system.fs.listFilesInDir(self._jpackage.getPathActions(), filter='*.py'):
            name=j.system.fs.getBaseName(path)
            if name[0]=="_":
                continue
            name=name[:-3]
            modname = "jpactions_%s" % j.tools.hash.md5_string(path)
            module = imp.load_source(modname, path)
            self._actions[name]= module.main
            name2=name.replace(".","_")
            self.__dict__[name2]=self._getActionMethod(name)

    def clear(self):
        self._done={}
        
    def _getActionMethod(self,name):
        found=False
        for item in ["kill","start","stop","monitor"]:
            if name.find(item)<>-1:
                found=True
        if found==True:
            C="""
def method(self{args}):
    result=self._actions['{name}'](j,self._jpackage{args})
    return result"""

        else:
            C="""
def method(self{args}):
    key="%s_%s_{name}"%(self._jpackage.domain,self._jpackage.name)
    if self._done.has_key(key):
        print "already executed %s"%key
        return True
    result=self._actions['{name}'](j,self._jpackage{args})
    self._done[key]=True
    return result"""

        args=""

        if name=="code.link" or name=="code.update":
            args=",force=False"

        elif name=="data.export" or name=="data.import":
            args=",url=None"       

        elif name=="monitor.up.net":
            args=",ipaddr='localhost'"       

        C=C.replace("{args}",args)
        C=C.replace("{name}",name)
        exec(C)
        return MethodType(method, self, ActionManager)

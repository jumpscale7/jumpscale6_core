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
           
            md5 = j.tools.hash.md5_string(path)
            modname = "JumpScale.baselib.jpackages.%s" % md5
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
    try:
        result=self._actions['{name}'](j,self._jpackage{args})
    except Exception,e:
        j.errorconditionhandler.processPythonExceptionObject(e)
        j.application.stop(1)
    return result"""

        else:
            C="""
def method(self{args}):
    key="%s_%s_{name}"%(self._jpackage.domain,self._jpackage.name)
    if self._done.has_key(key):
        print "already executed %s"%key
        return True
    try:
        result=self._actions['{name}'](j,self._jpackage{args2})
    except Exception,e:
        j.errorconditionhandler.processPythonExceptionObject(e)
        j.application.stop(1)
    self._done[key]=True
    return result"""

        args=""
        args2=""

        if name=="code.link" or name=="code.update":
            args=",force=True"
            args2=",force=force"

        elif name=="install.download":
            args=",expand=True,nocode=False"
            args2=",expand=expand,nocode=nocode"

        elif name=="upload":
            args=",onlycode=False"
            args2=",onlycode=onlycode"

        elif name=="data.export" or name=="data.import":
            args=",url=None"       
            args2=",url=url"

        elif name=="monitor.up.net":
            args=",ipaddr='localhost'"       
            args2=",ipaddr=ipaddr"

        C=C.replace("{args}",args)
        C=C.replace("{args2}",args2)
        C=C.replace("{name}",name)
        # print C
        exec(C)
        return MethodType(method, self, ActionManager)

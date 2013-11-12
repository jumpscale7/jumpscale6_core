from JumpScale import j

from types import MethodType

class ActionManager:
    """
    the action manager is responsible for executing the actions linked to a jpackages
    """

    def __init__(self,jp):
        print "init actions for %s"%jp
        self._jpackage=jp
        self._actions={}

        for path in j.system.fs.listFilesInDir(self._jpackage.getPathActions()):
            name=j.system.fs.getBaseName(path)
            if name[0]=="_":
                continue
            name=name[:-3]
            content=j.system.fs.fileGetContents(path)
            try:
                exec(content)
            except Exception as e:
                msg="Could not load action.script:%s\n" % path
                msg+="Error was:%s\n" % e
                # print msg
                j.errorconditionhandler.raiseInputError(msgpub="",message=msg,category="jpackages.actions.load",tags="",die=True)
                continue

            self._actions[name]=main
            name2=name.replace(".","_")
            self.__dict__[name2]=self._getActionMethod(name)
        
    def _getActionMethod(self,name):    
        C="""
def method(self{args}):
    return self._actions['{name}'](self._jpackage{args})"""

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

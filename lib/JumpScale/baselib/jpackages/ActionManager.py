from JumpScale import j

from types import MethodType

class ActionManager:
    """
    the action manager is responsible for executing the actions linked to a jpackages
    """

    def __init__(self,jpackages):
        self._jpackages=jpackages
        self.__te = None
        self._path=self._jpackages.getPathActions()
        self._taskletEngines={}

        for item in j.system.fs.listDirsInDir(self._path,dirNameOnly=True):
            item2=item.replace(".","_")
            self._taskletEngines[item2]=j.core.taskletengine.get(j.system.fs.joinPaths(self._path,item))
            self.__dict__[item2]=self._getActionMethod(item2)
        
    def _getActionMethod(self,name):    
        C="""
def method(self,**args):
    args["qp"]=self._jpackages
    te=self._taskletEngines["{name}"]
    result=te.executeV2(**args)
    return result
        """

        C=C.replace("{name}",name)
        exec(C)
        return MethodType(method, self, ActionManager)

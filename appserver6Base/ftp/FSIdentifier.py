from pylabs import q
from MetadataHandler import *
import os

class FSIdentifier():
    def __init__(self,root,usermanager):
        #self.root=q.system.fs.getFileExtension(root)
        self.usermanager=usermanager
        self.root=root
        self.identification={} #key = path, value =[$type,id,key]  $type:S,B  S=space, B=bucket


    #def _getConfigIdKey(self,path,isConfig=False):
        #if isConfig:
            #ini=q.tools.inifile.open(path)
        #else:
            #ini=q.tools.inifile.open(q.system.fs.joinPaths(path,"main.cfg"))
        #id=ini.getValue("main","id")
        #key=ini.getValue("main","key")
        #return id,key




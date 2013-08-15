from OpenWizzy import o
from MetadataHandler import *
import os

class FSIdentifier():
    def __init__(self,root,usermanager):
        #self.root=o.system.fs.getFileExtension(root)
        self.usermanager=usermanager
        self.root=root
        self.identification={} #key = path, value =[$type,id,key]  $type:S,B  S=space, B=bucket


    #def _getConfigIdKey(self,path,isConfig=False):
        #if isConfig:
            #ini=o.tools.inifile.open(path)
        #else:
            #ini=o.tools.inifile.open(o.system.fs.joinPaths(path,"main.cfg"))
        #id=ini.getValue("main","id")
        #key=ini.getValue("main","key")
        #return id,key




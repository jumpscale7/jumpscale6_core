#from OpenWizzy import o

#class MetadataHandler():

    #def __init__(self,root,usermanager):
        #self.root=root.replace("\\","/").strip("/").strip()
        #self.usermanager=usermanager
        #self.roots=["spaces","buckets","actors","root","stor"]
        #self.spaces={}

    #def normalizePath(self,path):
        #path=path.replace("\\","/")
        #path=path.lstrip("/")
        #path=path.rstrip("/")
        #return path

    #def ignorePath(self,item):
        ##items=[]
        ##for item in os.listdir(path):
        #ext=o.system.fs.getFileExtension(item)
        #if item.find(".quarantine")==0 or item.find(".tmb")==0:
            #o.system.fs.remove(item)
            #return True
        #elif ext=="pyc":
            #return True
        ##else:
            ##items.append(item)

    #def normalizePath(self,path):
        #path=path.replace("\\","/").strip("/").strip()
        #path=path.replace(self.root,"").strip("/")
        #return path

    #def getSubPath(self,path,type):
        #splitted=path.split("/")
        #pathfirst=splitted[0]
        #if pathfirst==type:
            #name=splitted[1].strip()
            #if len(splitted)>2:
                #splitted=splitted[1:]
                #postpath="/".join(splitted)
            #else:
                #postpath=""
        #return name,postpath


    ##def getPath(self,path):
        ##path0=path
        ##path=self.normalizePath(path)
        ##print "getpath %s"%path
        ##if path=="" or path==".":
            ##print "GETPATH ROOT"
            ##return ""
        ##if path in self.roots:
            ##print "GETPATH ROOTS /%s/"%path
            ##return ""
        ##for type in self.roots:
            ##name,postpath=self.getSubPath(path,type)
            ##if type=="space":

            ###self.root+"/"+self.normalizePath(path4)+"/"

        ##splitted=path.split("/")
        ##pathfirst=splitted[0]
        ##if pathfirst=="spaces":
            ##if self.spaces=={}:
                ##self.getSpaces()
            ##spacename=splitted[1].strip()
            ##path4=self.spaces[spacename]
            ##if len(splitted)>2:
                ##splitted=splitted[2:]
                ##path3="/".join(splitted)
            ##else:
                ##path3=""
            ##return self.root+"/"+self.normalizePath(path4)+"/"+path3



            ##from pylabs.Shell import ipshellDebug,ipshell
            ##print "DEBUG NOW space"
            ##ipshell()


        ##is not a special case so return input
        #return path

    #def listDir(self,path,fs=None):
        #path=self.normalizePath(path)
        #print "listdir:'%s'"%path
        #if path=="" or path=="." or path=="/":
            #return ["spaces","buckets","actors","root","stor"],"d"
        #if path.find("spaces")==0:
            #if path=="spaces":
                #self.getSpaces()
                #spaces=self.spaces.keys()
                #return spaces,"d"
            #else:
                #path5=path.replace("spaces/","")


                ##in spaces now need to return dir info
                #from pylabs.Shell import ipshellDebug,ipshell
                #print "DEBUG NOW uuuuuuuu"
                #ipshell()

        #if path.find("actors")==0:
            #return ["actors"],"d"
        #from pylabs.Shell import ipshellDebug,ipshell
        #print "DEBUG NOW h"
        #ipshell()

        #return ["nothing"],"d"
        #if path=="":
            #pass

    #def dirname2ftppath(self,dirname):
        #return "type=dir;size=0;perm=el;modify=20071127230206; %s"%dirname

from JumpScale import j
import JumpScale.baselib.codeexecutor
from HRD import *

class HRDTree():
    def __init__(self,path=""):
        self.items={} #link between key & hrd storing the key
        self.hrds=[] #all hrd's in tree
        if path<>"":
            self.add2tree(path)
        self.changed=False

    def add2treeFromContent(self,content):
        hrd=HRD("",treeposition,self)
        self.hrds.append(hrd)
        hrdpos=len(self.hrds)-1        
        hrd.process(content)

    def add2tree(self,path,recursive=True):
        # path=j.system.fs.pathNormalize(path)
        paths= j.system.fs.listFilesInDir(path, recursive=False, filter="*.hrd")
        
        for pathfound in paths:
            j.core.hrd.log("Add hrd %s" % (pathfound), level=7, category="load")                        
            hrd=HRD(pathfound,self)
            self.hrds.append(hrd)

    def exists(self,key):
        return self.items.has_key(key)

    def prefix(self, prefix):
        result=[]
        for hrd in self.hrds:
            for newkey in hrd.prefix(prefix):
                result.append(newkey)
        result.sort()
        return result

    def getListFromPrefix(self, prefix):
        """
        returns values from prefix return as list
        """
        result=[]
        for key in self.prefix(prefix):
            hrd = self.getHrd(key)    
            result.append(hrd.get(key))
        return result
  
    def getDictFromPrefix(self, prefix):
        """
        returns values from prefix return as list
        """
        result={}
        for key in self.prefix(prefix):
            hrd = self.getHrd(key)    
            result[key]=hrd.get(key)
        return result


    def get(self,key,default=None):
        if default<>None and self.items.has_key(key)==False:
            return default
        if not self.items.has_key(key):
            j.events.inputerror_critical("Cannot find %s in hrdtree."%key,"hrdtree.get.cannotfind")        
        return self.items[key].get()

    def getInt(self,key,default=None):
        if default<>None and self.items.has_key(key)==False:
            return default
        hrd=self.getHrd(key)
        return hrd.getInt(key)

    def getFloat(self,key,default=None):
        if default<>None and self.items.has_key(key)==False:
            return default
        hrd=self.getHrd(key)
        return hrd.getFloat(key)

    def getBool(self,key,default=None):
        if default<>None and self.items.has_key(key)==False:
            return default
        hrd=self.getHrd(key)
        return hrd.getBool(key)

    # def getList(self,key,default=None):
    #     if default<>None and self.items.has_key(key)==False:
    #         return default        
    #     hrd=self.getHrd(key)
    #     return hrd.getList(key)

    # def getDict(self,key,default=None):
    #     if default<>None and self.items.has_key(key)==False:
    #         return default        
    #     hrd=self.getHrd(key)
    #     return hrd.getDict(key)

    # def setDict(self,key,ddict):                
    #     hrd=self.getHrd(key)
    #     return hrd.setDict(key,ddict)

    def getHrd(self,key):
        if not self.items.has_key(key):
            j.events.inputerror_critical("Cannot find key:'%s' in tree"%key,"hrdtree.gethrd.notfound")
        return self.items[key].hrd

    def set(self,key,val,persistent=True):
        hrd=self.getHrd(key)
        hrd.set(key,val,persistent=persistent)

    def applyOnDir(self,path,filter=None, minmtime=None, maxmtime=None, depth=None,changeFileName=True,changeContent=True,additionalArgs={}):
        """
        look for $(name) and replace with hrd value
        """
        j.core.hrd.log("hrd:%s apply on dir:%s in position:%s"%(self.path,path,position),category="apply")
        
        items=j.system.fs.listFilesInDir( path, recursive=True, filter=filter, minmtime=minmtime, maxmtime=maxmtime, depth=depth)
        for item in items:
            if changeFileName:
                item2=self._.replaceVarsInText(item,additionalArgs=additionalArgs)
                if item2<>item:
                     j.system.fs.renameFile(item,item2)
                    
            if changeContent:
                self.applyOnFile(item2,position=position,additionalArgs=additionalArgs)

    def applyOnFile(self,path,additionalArgs={}):
        """
        look for $(name) and replace with hrd value
        """

        j.core.hrd.log("hrd:%s apply on file:%s in position:%s"%(self.path,path,position),category="apply")
        content=j.system.fs.fileGetContents(path)
        content=self._replaceVarsInText(content,additionalArgs=additionalArgs)
        j.system.fs.writeFile(path,content)

    def applyOnContent(self,content,additionalArgs={}):
        """
        look for $(name) and replace with hrd value
        """

        content=self._replaceVarsInText(content,self,position,additionalArgs=additionalArgs)
        return content

    def _replaceVarsInText(self,content,additionalArgs={}):
        if content=="":
            return content
            
        items=j.codetools.regex.findAll(r"\$\([\w.]*\)",content)
        j.core.hrd.log("replace vars in hrdtree:%s"%hrdtree.path,"replacevar",7)
        if len(items)>0:
            for item in items:
                # print "look for : %s"%item
                item2=item.strip(" ").strip("$").strip(" ").strip("(").strip(")")

                if additionalArgs.has_key(item2.lower()):
                    newcontent=additionalArgs[item2.lower()]
                else:
                    newcontent=self.get(item2,checkExists=True)
                # print "nc:%s"%newcontent
                content=content.replace(item,newcontent)                 
        return content        

    def __repr__(self):
        parts=[]
        keys=self.items.keys()
        keys.sort()
        out=""
        for key in keys:
            hrditem=self.items[key]            
            if hrditem.comments<>"":
                out+="\n%s\n" % (hrditem.comments.strip())
            out+="%s = %s\n" % (key, hrditem.getValOrDataAsStr())
        return out

    def __str__(self):
        return self.__repr__()

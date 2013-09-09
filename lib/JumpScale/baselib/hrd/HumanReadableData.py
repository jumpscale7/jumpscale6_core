from JumpScale import j

class HumanReadableDataFactory:
    def __init__(self):
        pass

    def getHRDTree(self,path="",content=""):
        """
        @param path
        """
        return HumanReadableDataTree(path,content)

    def getHRDFromContent(self,content=""):
        """
        @param path
        """
        return HRD(content=content)


    def replaceVarsInText(self,content,hrdtree,position=""):
        items=j.codetools.regex.findAll(r"\$\([\w.]*\)",content)
        
        if len(items)>0:
            for item in items:
                # print "look for : %s"%item
                item2=item.strip(" ").strip("$").strip(" ").strip("(").strip(")")

                if position<>"":
                
                    newcontent=hrdtree.get(item2,position=position,checkExists=True)
                else:
                    newcontent=hrdtree.get(item2,checkExists=True)

                # print "nc:%s"%newcontent
                if newcontent<>False:
                    content=content.replace(item,newcontent)
        return content

    def getHRDFromOsisObject(self,osisobj,prefixRootObjectType=True):
        txt=j.db.serializers.hrd.dumps(osisobj.obj2dict())
        prefix=osisobj._P__meta[2]
        out=""
        for line in txt.split("\n"):
            if line.strip()=="":
                continue
            if line[0]=="_":
                continue
            if line.find("_meta.")<>-1:
                continue
            if prefixRootObjectType:
                out+="%s.%s\n"%(prefix,line)
            else:
                out+="%s\n"%(line)
        return self.getHRDFromContent(out)        


        

class HRDPos():
    def __init__(self,treeposition,tree):
        self._key2hrd={}
        self._hrds={}
        self._tree=tree
        self._treeposition=  treeposition  

    def set(self,key,value,persistent=True):

        key2=self._normalizeKey(key)
        # print "set:'%s':'%s'"%(key,value)        
        self.__dict__[key2]=value
        if persistent==True:
            hrd=self.getHRD(key)
            hrd.set(key,value,persistent)
            print "set in hrdpos %s in hrdfile %s: %s %s"%(self._treeposition,hrd._path,key,value)

    def getHRD(self,key):
        key=key.replace(".","_")
        if not self._key2hrd.has_key(key):
            j.errorconditionhandler.raiseBug(message="Cannot find hrd on position '%s'"%(self._treeposition),category="osis.gethrd")
        return self._hrds[self._key2hrd[key]]

    def addHrdItem(self,hrd,hrdpos):
        self._hrds[hrdpos]=hrd
        for key in [item for item in hrd.__dict__.keys() if item[0]<>"_"]:
            self.__dict__[key]=hrd.__dict__[key]
            self._key2hrd[key]=hrdpos

    def _normalizeKey(self,key):
        return str(key).lower().replace(".","_")

    def get(self,key,checkExists=False):
        key=self._normalizeKey(key)
        if not self.__dict__.has_key(key):
            if checkExists:
                return False
            raise RuntimeError("Cannot find value with key %s in tree %s."%(key,self._tree.path))

        val=self.__dict__[key]

        if str(val).find("$(")<>-1:
            items=j.codetools.regex.findAll(r"\$\([\w.]*\)",val)
            for item in items:
                #param found which needs to be filled in
                item2=item.replace("(","").replace(")","").replace("$","").strip()
                val2=self.get(item2)
                val=val.replace(item,val2)
                self.set(key,val,persistent=False)
        return val

    def getBool(self,key):
        res=self.getInt(key)
        if res==1:
            return True
        else:
            return False

    def getList(self,key):
        res=self.get(key)
        return res.split(",")

    def getDict(self,key):
        res=self.get(key)
        res2={}
        for item in res.split(","):
            if item.strip()<>"":
                key,val=item.split(":")
                res2[key]=val
        return res2

    def getInt(self,key):
        res=self.get(key)
        if j.basetype.string.check(res):
            if res.lower()=="none":
                res=0
            elif res=="":
                res=0
            else:
                res=int(res)
        else:
            res=int(res)
        return res

    def getFloat(self,key):
        res=self.get(key)
        return float(res)

    def exists(self,key):
        key=key.lower()
        return self.__dict__.has_key(key)

    def __repr__(self):
        parts = []
        parts.append("treeposition:%s"%self._treeposition)
        keys=self.__dict__.keys()
        keys.sort()
        for key in keys:
            if key[0]<>"_":
                value=self.__dict__[key]
                if key not in ["tree","treeposition","path"]:
                    key=key.replace("_",".")
                    if key[-1]==".":
                        key=key[:-1]                    
                    parts.append(" %s:%s" % (key, value))
        return "\n".join(parts)

    def __str__(self):
        return self.__repr__()



class HRD():
    def __init__(self,path="",treeposition="",tree=None,content=""):
        self._path=path
        self._tree=tree
        self._treeposition=  treeposition
        if content:
            self.process(content)

    def _serialize(self,value):
        if j.basetype.string.check(value):
            value=value.replace("\n","\\n")    
        elif j.basetype.boolean.check(value):
            if value==True:
                value="1"
            else:
                value="0"
        elif j.basetype.list.check(value):
            valueout=""
            for item in value:
                valueout+="%s,"%item
            value=valueout.strip(",")                 
        elif j.basetype.dictionary.check(value):
            valueout=""
            test={}
            for key in value.keys():                    
                key=str(key)
                if not test.has_key(key):
                    valueout+="%s:%s,"%(key,str(value[key]))
                test[key]=1
            value=valueout.strip(",")        
        return value

    def _unserialize(self,value):
        value=value.replace("\\n","\n")    
        return value

    def set(self,key,value,persistent=True):
        key=key.lower()
        key2=key.replace(".","_")
        self.__dict__[key2]=value
        if persistent==True:
            value=self._serialize(value)
            self._set(key,value)
            # print "set in hrd itself: %s %s"%(key,value)

    def _set(self,key,value):
        out=""
        comment="" 
        keyfound = False
        for line in j.system.fs.fileGetContents(self._path).split("\n"):
            line=line.strip()
            if line=="" or line[0]=="#":
                out+=line+"\n"
                continue
            if line.find("=")<>-1:
                #found line
                if line.find("#")<>-1:
                    comment=line.split("#",1)[1]
                    line2=line.split("#")[0]                    
                else:
                    line2=line
                key2,value2=line2.split("=",1)
                if key2.lower().strip()==key:
                    keyfound = True
                    if comment<>"":
                        line="%s=%s #%s"%(key,value,comment)
                    else:
                        line="%s=%s"%(key,value)
            comment=""
            out+=line+"\n"

        out = out.strip('\n') + '\n'
        if not keyfound:
            out+="%s=%s\n" % (key, value)

        j.system.fs.writeFile(self._path,out)

    def write(self, path=None):
        C=""
        for key0 in self.__dict__:
            if key0[0]=="_":
                continue
            key=key0.replace("_",".")
            C+="%s=%s\n"%(key,self.__dict__[key0])
        if path:
            j.system.fs.writeFile(path,C)
        else:
            self._fixPath()
            j.system.fs.createDir(j.system.fs.getDirName(self._path))
            j.system.fs.writeFile(self._path,C)        
                
    def _fixPath(self):
        self._path=self._path.replace(":","")
        self._path=self._path.replace("  "," ")

    def get(self,key,checkExists=False):
        key=key.lower()
        key2=key.replace(".","_")        
        if not self.__dict__.has_key(key2):
            if checkExists:
                return False
            raise RuntimeError("Cannot find value with key %s in tree %s."%(key,self._tree.path))

        val= self.__dict__[key2]

        content=self._unserialize(val)
        return str(content).strip()

    def getBool(self,key):
        res=self.get(key)
        if res==1:
            return True
        else:
            return False

    def getList(self,key):
        res=self.get(key)
        return res.split(",")

    def getDict(self,key):
        res=self.get(key)
        res2={}
        for item in res.split(","):
            if item.strip()<>"":
                key,val=item.split(":")
                res2[key]=val
        return res2

    def getInt(self,key):
        res=self.get(key)
        return int(res)

    def getFloat(self,key):
        res=self.get(key)
        return float(res)

    def exists(self,key):
        key=key.lower()
        return self.__dict__.has_key(key)

    def read(self):
        content=j.system.fs.fileGetContents(self._path)
        self.process(content)

    def process(self,content):
        for line in content.split("\n"):
            line=line.strip()
            if line=="" or line[0]=="#":
                continue
            if line.find("=")<>-1:
                #found line
                if line.find("#")<>-1:
                    line=line.split("#")[0]
                key,value=line.split("=",1)
                key=key.strip().lower()
                value=value.strip()
                self.set(key,value,persistent=False)


    def getPath(self,key):
        return j.core.hrd.getPath(self._paths[key])


    def pop(self,key):
        if self.has_key(key):
            self.__dict__.pop(key)

    def has_key(self, key):
        return self.__dict__.has_key(key)

    def setDict(self,dictObject):
        self.__dict__.update(dictObject)

    def __repr__(self):
        # parts = ["path:%s"%self._path]
        # parts.append("treeposition:%s"%self._treeposition)
        parts=[]
        keys=self.__dict__.keys()
        keys.sort()
        for key in keys:
            value=self.__dict__[key]
            if key[0]<>"_":
                key=key.replace("_",".")
                if key[-1]==".":
                    key=key[:-1]
                parts.append(" %s:%s" % (key, value))
        return "\n".join(parts)

    def __str__(self):
        return self.__repr__()


class HumanReadableDataTree():
    def __init__(self,path="",content=""):
        self.positions={}
        self.hrds=[]
        self.hrdpaths={}
        if path<>"":
            self.path=j.system.fs.pathNormalize(path)        
            self.add2tree(self.path)
        else:
            self.path=None
        if content<>"":
            self.add2treeFromContent(content)

    def getPosition(self,startpath,curpath,position=""):  
        position=position.strip("/")
        # curpath=j.system.fs.getDirName(curpath+"/")
        # print "path:%s"%self.path
        key=j.system.fs.pathRemoveDirPart(curpath,startpath,True)
        if position not in key:
            res="%s/%s"%(position,key)
        else:
            res=key
        res=res.replace("\\","/").replace("//","/")
        return res.strip("/")


    def add2treeFromContent(self,content,treeposition=""):
        self.positions[treeposition]=HRDPos(treeposition,self)
        hrdposObject=self.positions[treeposition]
        hrd=HRD("",treeposition,self)
        self.hrds.append(hrd)
        hrdpos=len(self.hrds)-1        
        hrd.process(content)
        hrdposObject.addHrdItem(hrd,hrdpos=hrdpos) 

    def add2tree(self,path,recursive=True,position="",startpath=""):
        path=j.system.fs.pathNormalize(path)
        if startpath=="":
            startpath=path
        # self.positions[startpoint]=[HRD(path,startpoint,self)]

        paths= j.system.fs.listFilesInDir(path, recursive=False, filter="*.hrd")
        
        treeposition=self.getPosition(startpath,path,position)

        if not self.positions.has_key(treeposition):
            self.positions[treeposition]=HRDPos(treeposition,self)

        hrdposObject=self.positions[treeposition]

        for pathfound in paths:
            j.logger.log("Add hrd %s from %s to position:'%s'" % (pathfound,startpath,treeposition), level=9, category="hrd.load")
                        
            hrd=HRD(pathfound,treeposition,self)
            hrd.read()

            self.hrds.append(hrd)
            hrdpos=len(self.hrds)-1
            self.hrdpaths[hrd._path]=hrdpos

            for hrdparent in self.getParentHRDs(treeposition):
                hrdposObject.addHrdItem(hrdparent,hrdpos=hrdpos)
            hrdposObject.addHrdItem(hrd,hrdpos=hrdpos)            

        if recursive:
            dirs= j.system.fs.listDirsInDir(path, recursive=False)
            for ddir in dirs:
                self.add2tree(ddir,recursive=recursive,position=treeposition,startpath=startpath)

    def getParentHRDs(self,treeposition):
        res={}
        for poskey in self.positions.keys():
            pos=self.positions[poskey]
            treeposition2=pos._treeposition
            if treeposition2 in treeposition and treeposition2<>treeposition:
                for hrdid in pos._hrds.keys():
                    res[hrdid]=pos._hrds[hrdid]
        res2=[]
        for key in res.keys():
            res2.append(res[key])
            
        return res2

    def exists(self,key,position=""):
        hrd = self.getHrd(position,True)
        if not hrd:
            return False
        return hrd.exists(key)

    def get(self,key,position="",checkExists=False):
        hrd=self.getHrd(position,checkExists=checkExists)
        if checkExists:
            if hrd==False:
                return False
        val=hrd.get(key,checkExists=checkExists)
        if checkExists:
            if val==False:
                return False
        return val

    def getInt(self,key,position=""):
        hrd=self.getHrd(position)
        return hrd.getInt(key)

    def getFloat(self,key,position=""):
        hrd=self.getHrd(position)
        return hrd.getFloat(key)

    def getBool(self,key,position=""):
        hrd=self.getHrd(position)
        return hrd.getBool(key)

    def getList(self,key,position=""):
        hrd=self.getHrd(position)
        return hrd.getList(key)

    def getDict(self,key,position=""):
        hrd=self.getHrd(position)
        return hrd.getDict(key)

    def getHrd(self,position="",checkExists=False):
        position=position.strip("/")
        if not self.positions.has_key(position):
            if checkExists:
                return False
            raise RuntimeError("Cannot find position %s in tree %s."%(position,self.path))

        orgpos=position
        hrd=self.positions[position]
        # x=0
        # while not hrd.exists(key):
        #     # print "search:%s pos:%s\n%s\n\n"%(key,position,hrd)
        #     #look for next in array on position
        #     if x<len(self.positions[position])-1:
        #         x+=1
        #         hrd=self.positions[position][x]
        #     #look for position higher
        #     elif position.find("/")<>-1:
        #         x=0
        #         position="/".join(position.split("/")[:-1])
        #         hrd=self.positions[position][0]
        #     #rootposition
        #     elif position.strip()<>"":
        #         x=0
        #         position=""
        #         hrd=self.positions[position][0]
        #     else:
        #         if checkExists:
        #             return False
        #         raise RuntimeError("Cannot find value with key %s in tree %s on position:%s"%(key,self.path,orgpos))
        return hrd

    def set(self,key,val,position=""):
        hrd=self.getHrd(position)
        hrd.set(key,val,persistent=True)
        print "hrdset: %s %s"%(key,val)

    def applyOnDir(self,path,position="",filter=None, minmtime=None, maxmtime=None, depth=None,changeFileName=True,changeContent=True):
        print "apply on dir: %s in position:%s"%(path,position)
        
        items=j.system.fs.listFilesInDir( path, recursive=True, filter=filter, minmtime=minmtime, maxmtime=maxmtime, depth=depth)
        for item in items:
            if changeFileName:
                item2=j.core.hrd.replaceVarsInText(item,self,position)
                if item2<>item:
                     j.system.fs.renameFile(item,item2)
                    
            if changeContent:
                self.applyOnFile(item2,position=position)

    def applyOnFile(self,path,position=""):
        content=j.system.fs.fileGetContents(path)
        content=j.core.hrd.replaceVarsInText(content,self,position)
        j.system.fs.writeFile(path,content)

    def __repr__(self):
        parts = []
        for key, value in self.positions.iteritems():
            parts.append(str(value)+'\n')
        return "\n".join(parts)

    def __str__(self):
        return self.__repr__()

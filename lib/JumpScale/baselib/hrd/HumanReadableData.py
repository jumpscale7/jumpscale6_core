from JumpScale import j
import JumpScale.baselib.codeexecutor

class HumanReadableDataFactory:
    def __init__(self):
        self.logenable=True
        self.loglevel=5

    def log(self,msg,category="",level=5):
        if level<self.loglevel+1 and self.logenable:
            j.logger.log(msg,category="hrd.%s"%category,level=level)

    def getHRD(self,path="",content=""):
        """
        @param path
        """
        if content<>"":
            return HRD(content=content)            
        if j.system.fs.isDir(path):
            return HumanReadableDataTree(path,content)

        return HRD(path=path)        

    def _normalizeKey(self,key):
        return str(key).lower().replace(".","_")

    def replaceVarsInText(self,content,hrdtree,position=""):
        if content=="":
            return content
            
        items=j.codetools.regex.findAll(r"\$\([\w.]*\)",content)
        j.core.hrd.log("replace vars in hrdtree:%s"%hrdtree.path,"replacevar",7)
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
                # else:
                #     print "notfound:%s"%item
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
        self._key2hrd={}  #key to position (does not work when new keys in e.g. set)
        self._hrds={} #id of hrd(file) to the hrd
        self._tree=tree
        self._treeposition=  treeposition
        self.changed=False

    def set(self,key,value,persistent=True,position=""):

        key2=j.core.hrd._normalizeKey(key)
        # print "set:'%s':'%s'"%(key,value)        
        self.__dict__[key2]=value
        if persistent==True:
            hrd=self.getHRD(key,position)
            hrd.set(key,value,persistent)

    def getHRD(self,key,position=""):
        if len(self._hrds.keys())==1:
            return self._hrds[self._hrds.keys()[0]]
        key=key.replace(".","_")
        if key not in self._key2hrd:
            self._reloadCache()
            if key not in self._key2hrd:
                j.errorconditionhandler.raiseBug(message="Cannot find hrd on position '%s'"%(self._treeposition),category="osis.gethrd")
        return self._hrds[self._key2hrd[key]]

    def _reloadCache(self):
        self._key2hrd = dict()
        for pos, hrd in self._hrds.iteritems():
            self.addHrdItem(hrd, pos)

    def addHrdItem(self,hrd,hrdpos):
        self._hrds[hrdpos]=hrd
        for key in [item for item in hrd.__dict__.keys() if (len(item)>0 and item[0]<>"_") ]:
            self.__dict__[key]=hrd.__dict__[key]
            self._key2hrd[key]=hrdpos

    def get(self,key,checkExists=False):
        key=j.core.hrd._normalizeKey(key)        
        if key not in self.__dict__:
            self._reloadCache()
            if key not in self.__dict__:
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

        j.core.hrd.log("get in hrd:%s '%s':'%s'"%(self._tree.path,key,val),category="get",level=6)

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

    def prefix(self, key):
        key = j.core.hrd._normalizeKey(key)
        for knownkey in self.__dict__.keys():
            # print "prefix: %s - %s"%(knownkey,key)
            if knownkey.startswith(key):
                yield knownkey.replace('_', '.')

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
        key=key.replace(".","_")        
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
        self.path=self._path
        self._tree=tree
        self._treeposition=  treeposition
        self.process(content)
        self.changed=False

    def _markChanged(self):
        self.changed=True
        if self._tree<>None:
            self._tree.changed=True
        # if self._treeposition<>None:
        #     self._treeposition.changed=True


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
            j.core.hrd.log("set in hrd:%s '%s':'%s'"%(self._path,key,value),category="set")
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

    def prefix(self, key):
        key = j.core.hrd._normalizeKey(key)
        for knownkey in self.__dict__.keys():
            # print "prefix: %s - %s"%(knownkey,key)
            if knownkey.startswith(key):
                yield knownkey.replace('_', '.')

    def get(self,key,checkExists=False):
        key=key.lower()
        key2=key.replace(".","_")        
        if not self.__dict__.has_key(key2):
            if checkExists:
                return False
            raise RuntimeError("Cannot find value with key %s in tree %s."%(key,self.path))

        val= self.__dict__[key2]

        content=self._unserialize(val)
        val=str(content).strip()
        j.core.hrd.log("hrd:%s get '%s':'%s'"%(self._path,key,val))
        return val

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
        key=key.replace(".","_")
        key=key.lower()
        return self.__dict__.has_key(key)

    def read(self):
        content=j.system.fs.fileGetContents(self._path)
        self.process(content)

    def _ask(self,name,value):
        self._markChanged()
        value=value.replace("@ASK","").strip()
        tags=j.core.tags.getObject(value)

        if tags.tagExists("name"):
            name=tags.tagGet("name")

        if tags.tagExists("type"):
            ttype=tags.tagGet("type").strip().lower()
            if ttype=="string":
                ttype="str"
        else:
            ttype="str"
        if tags.tagExists("descr"):
            descr=tags.tagGet("descr")
        else:
            descr="Please provide value for %s"%name

        name=name.replace("__"," ")

        descr=descr.replace("__"," ")
        descr=descr.replace("\\n","\n")

        if tags.tagExists("default"):
            default=tags.tagGet("default")
        else:
            default=""

        if ttype=="str":
            result=j.console.askString(question=descr, defaultparam=default, regex=None)

        elif ttype=="float":
            result=j.console.askString(question=descr, defaultparam=default, regex=None)
            #check getFloat
            try:
                result=float(result)
            except:
                raise RuntimeError("Please provide float.")
            result=str(result)
        
        elif ttype=="int":
            result=str(j.console.askInteger(question=descr, defaultValue=default))

        elif ttype=="bool":
            if descr<>"":
                print descr
            result=j.console.askYesNo()
            if result:
                result=1
            else:
                result=0

        elif ttype=="dropdown":
            if tags.tagExists("dropdownvals"):
                dropdownvals=tags.tagGet("dropdownvals")
            else:
                raise RuntimeError("When type is dropdown in ask, then dropdownvals needs to be specified as well.")
            choicearray=dropdownvals.split(",")
            result=j.console.askChoice(choicearray, descr=descr, sort=True)

        else:
            raise RuntimeError("Input type:%s is invalid (only: bool,int,str,string,dropdown,float)")

        return result
        
    def checkValidity(self,template):
        """
        @param template is example hrd which will be used to check against, if params not found will be added to existing hrd and error will be thrown to allow user to configure settings
        """
        error=False
        for line in template.split("\n"):
            line=line.strip()
            if line=="" or line[0]=="#":
                continue
            if line.find("=")<>-1:
                items=line.split("=")
                if len(items)>2:
                    raise RuntimeError("in template only 1 '=' sign' per line")
                key=items[0].strip()
                defvalue=items[1].strip()
                if not self.exists(key):
                    error=True
                    self.set(key,defvalue)
                    self.changed = True
        if error:
            self.process()

    def process(self,content=""):
        if content=="":
            content=j.system.fs.fileGetContents(self._path)
        content=j.codetools.executor.eval(content)
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
                self.changed = True
                if value.find("@ASK")<>-1:
                    if not j.application.shellconfig.interactive:
                        raise RuntimeError("Can ask key %s interactively. Config file was not complete, please change the default values of config file at location %s"% (key, self._path))

                    value=self._ask(key,value)
                    self.set(key,value,persistent=True)
                else:
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

    def applyOnDir(self,path,filter=None, minmtime=None, maxmtime=None, depth=None,changeFileName=True,changeContent=True):
        j.core.hrd.log("hrd:%s apply on dir:%s "%(self._path,path),category="apply")
        
        items=j.system.fs.listFilesInDir( path, recursive=True, filter=filter, minmtime=minmtime, maxmtime=maxmtime, depth=depth)
        for item in items:
            if changeFileName:
                item2=j.core.hrd.replaceVarsInText(item,self)
                if item2<>item:
                     j.system.fs.renameFile(item,item2)
                    
            if changeContent:
                self.applyOnFile(item2)

    def applyOnFile(self,path):
        j.core.hrd.log("hrd:%s apply on file:%s"%(self.path,path),category="apply")
        content=j.system.fs.fileGetContents(path)

        content=j.core.hrd.replaceVarsInText(content,self)
        j.system.fs.writeFile(path,content)

    def applyOnContent(self,content):
        content=j.core.hrd.replaceVarsInText(content,self)
        return content

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
        self.changed=False

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

            j.core.hrd.log("Add hrd %s to position:'%s'" % (pathfound,treeposition), level=7, category="load")
                        
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

    def prefix(self, key, position=None):
        if position is None:
            hrds = [self.getHrd(x) for x in self.positions.keys() ]
        else:
            hrds = [ self.getHrd(position) ]
        for hrd in hrds:
            for newkey in hrd.prefix(key):
                yield newkey

    def getItemsFromPrefix(self, prefix, position=None):
        if position is None:
            hrds = [self.getHrd(x) for x in self.positions.keys() ]
        else:
            hrds = [ self.getHrd(position) ]
        result=[]
        for hrd in hrds:
            for newkey in hrd.prefix(prefix):
                result.append(hrd.get(newkey))
        return result

    def get(self,key,position="",checkExists=False,defaultval=False):
        hrd=self.getHrd(position,checkExists=checkExists)
        if checkExists:
            if hrd==False:
                return defaultval
        val=hrd.get(key,checkExists=checkExists)
        if checkExists:
            if val==False:
                return defaultval
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

    def applyOnDir(self,path,position="",filter=None, minmtime=None, maxmtime=None, depth=None,changeFileName=True,changeContent=True):
        j.core.hrd.log("hrd:%s apply on dir:%s in position:%s"%(self.path,path,position),category="apply")
        
        items=j.system.fs.listFilesInDir( path, recursive=True, filter=filter, minmtime=minmtime, maxmtime=maxmtime, depth=depth)
        for item in items:
            if changeFileName:
                item2=j.core.hrd.replaceVarsInText(item,self,position)
                if item2<>item:
                     j.system.fs.renameFile(item,item2)
                    
            if changeContent:
                self.applyOnFile(item2,position=position)

    def applyOnFile(self,path,position=""):
        j.core.hrd.log("hrd:%s apply on file:%s in position:%s"%(self.path,path,position),category="apply")
        content=j.system.fs.fileGetContents(path)

        content=j.core.hrd.replaceVarsInText(content,self,position)
        j.system.fs.writeFile(path,content)

    def applyOnContent(self,content,position=""):
        content=j.core.hrd.replaceVarsInText(content,self,position)
        return content

    def __repr__(self):
        parts = []
        for key, value in self.positions.iteritems():
            parts.append(str(value)+'\n')
        return "\n".join(parts)

    def __str__(self):
        return self.__repr__()

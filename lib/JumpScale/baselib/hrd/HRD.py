from JumpScale import j
import JumpScale.baselib.codeexecutor

class HRDItem():
    def __init__(self,name,hrd,ttype,data,comments):
        """
        @ttype: normal,dict,list
        normal can be : int, str, float,bool
        """
        self.hrd=hrd
        self.ttype=ttype
        self.name=name
        self.data=data
        self.value=None
        self.comments=comments        

    def get(self):
        if self.value==None:
            self._process()
        return self.value

    def getValOrDataAsStr(self):
        if self.value<>None:
            return j.tools.text.pythonObjToStr(self.value)
        elif self.data.lower().find("@ask")==-1:
            self._process()
            return j.tools.text.pythonObjToStr(self.value)
        else:
            return self.data.strip()

    def set(self,value,persistent=True,comments=""):
        self.value=value
        if comments<>"":
            self.comments=comments
        self.hrd._markChanged()
        if self.hrd.keepformat:
            state="start"
            out=""
            found=False
            for line in j.system.fs.fileGetContents(self.hrd.path).split("\n"):
                if line.strip().startswith(self.name):                        
                    state="found"
                    continue

                if state=="found" and (len(line)==0 or line[0]==" "):
                    continue

                if state=="found":
                    state="start"
                    #now add the var
                    found=True
                    if self.comments<>"":
                        out+="%s\n" % (self.comments)
                    out+="%s = %s\n" % (self.name, self.getValOrDataAsStr())

                out+="%s\n"%line

            if found==False:
                if self.comments<>"":
                    out+="%s\n" % (self.comments)
                out+="%s = %s\n" % (self.name, self.getValOrDataAsStr())

            if persistent:
                j.system.fs.writeFile(filename=self.hrd.path,contents=out)

        else:
            if persistent:
                self.hrd.save()

    def _process(self):
        value2=j.tools.text.ask(self.data)
        self.value=j.tools.text.hrd2machinetext(value2)
        if self.ttype=="dict":
            currentobj={}
            self.value=self.value.rstrip(",")
            for item in self.value.split(","):
                key,post2=item.split(":",1)                                    
                currentobj[key.strip()]=post2.strip()
            self.value=j.tools.text.str2var(currentobj)
        elif self.ttype=="list":
            self.value=self.value.rstrip(",")
            currentobj=[]
            for item in self.value.split(","):
                currentobj.append(item.strip())
            self.value=j.tools.text.str2var(currentobj)
        else:
            self.value=j.tools.text.str2var(self.value)

    def __str__(self):
        return "%-15s|%-5s|'%s' -- '%s'"%(self.name,self.ttype,self.data,self.value)

    __repr__=__str__

class HRD():
    def __init__(self,path="",tree=None,content=""):
        self.path=path
        self.name=".".join(j.system.fs.getBaseName(self.path).split(".")[:-1])
        self.tree=tree
        self.changed=False
        self.items={}
        self.commentblock=""  #at top of file
        self.keepformat=True
        self.prepend=""
        self.template=""

        if content<>"":
            self.process(content)
        else:
            self.read()

    def _markChanged(self):
        self.changed=True
        if self.tree<>None:
            self.tree.changed=True

    def set(self,key,value,persistent=True,comments=""):
        """
        """
        key=key.lower()
        if not self.items.has_key(key):
            self.items[key]=HRDItem(name=key,hrd=self,ttype="base",data=value,comments="")    
        self.items[key].set(value,persistent=persistent,comments=comments)

    def save(self):   
        j.system.fs.writeFile(self.path,str(self))

    def delete(self,key):
        if self.items.has_key(key):
            self.items.pop(key)

        out=""

        for line in j.system.fs.fileGetContents(self.path).split("\n"):
            delete=False
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
                    delete = True

            comment=""
            if delete<>True:
                out+=line+"\n"

        out = out.strip('\n') + '\n'

        j.system.fs.writeFile(self.path,out)

    def prefix(self, key):
        result=[]
        for knownkey in self.items.keys():
            # print "prefix: %s - %s"%(knownkey,key)
            if knownkey.startswith(key):
                result.append(knownkey)
        result.sort()                
        return result

    def get(self,key,default=None,):

        if not self.items.has_key(key):
            if default==None:
                j.events.inputerror_critical("Cannot find value with key %s in tree %s."%(key,self.path),"hrd.get.notexist")
            else:
                self.set(key,default)
                return default
        val= self.items[key].get()
        j.core.hrd.log("hrd:%s get '%s':'%s'"%(self.path,key,val))
        return val

    def getBool(self,key,default=None):
        res=self.get(key,default=default)
        if res=="1" or res.lower()=="true":
            return True
        else:
            return False            

    # def getList(self,key,default=None,deserialize=False):
    #     res=self.get(key,default=default)
    #     return j.tools.text.getList(res,deserialize=deserialize)

    # def getDict(self,key,default=None,deserialize=False):
    #     res=self.get(key,default=default)
    #     return j.tools.text.getDict(res,deserialize=deserialize)

    def setDict(self,key,ddict):        
        out=""
        for key2,value in ddict.iteritems():
            out+="%s:%s,"%(key2,value)
        out=out.rstrip(",")
        self.set(key,out)        

    def getInt(self,key,default=None):
        if default<>None:
            default=int(default)        
        res=self.get(key,default=default)
        return j.tools.text.getInt(res)

    def getFloat(self,key):
        res=self.get(key)
        return j.tools.text.getFloat(res)

    def exists(self,key):
        key=key.lower()
        return self.items.has_key(key)

    def getListFromPrefix(self, prefix):
        """
        returns values from prefix return as list
        """
        result=[]
        for key in self.prepend(prefix):
            result.append(self.get(key))
        return result
  
    def getDictFromPrefix(self, prefix):
        """
        returns values from prefix return as list
        """
        result={}
        for key in self.prepend(prefix):
            result[key]=self.get(key)
        return result

    def read(self):
        content=j.system.fs.fileGetContents(self.path)
        self.process(content)

    def checkValidity(self,template,hrddata={}):
        """
        @param template is example hrd which will be used to check against, 
        if params not found will be added to existing hrd 
        """            
        for line in template.split("\n"):
            line=line.strip()
            if line=="" or line[0]=="#":
                continue
            if line.find("=") != -1:
                items=line.split("=", 1)
                key=items[0].strip()
                defvalue=items[1].strip()
                # print "key:%s "%key
                if hrddata.has_key(key):
                    # print "set:%s"%hrddata[key]
                    self.set(key,hrddata[key])
                    self.changed = True
                elif not self.exists(key):
                    self.set(key,defvalue)
                    self.changed = True
                    # self.process()

    def _recognizeType(self,content):        
        content=j.tools.text.replaceQuotes(content,"something")
        if content.lower().find("@ask")<>-1:
            return "ask"
        elif content.find(":")<>-1:
            return "dict"
        elif content.find(",")<>-1:
            return "list"
        elif content.lower().strip().startswith("@ask"):
            return "ask"
        else:
            return "base"

    def applytemplate(self,path=""):
        if path=="":
            path=self.template
        if path<>"":
            hrdtemplate=HRD(path=path)
            for key in hrdtemplate.items.keys():
                if not self.items.has_key(key):
                    hrdtemplateitem=hrdtemplate.items[key]
                    self.set(hrdtemplateitem.name,hrdtemplateitem.data,comments=hrdtemplateitem.comments)

    def process(self,content):

        if content=="":
            content=j.system.fs.fileGetContents(self.path)        

        state="start"
        comments=""
        multiline=""
        self.content=content

        #find instructions
        for line in content.split("\n"):
            line2=line.strip()
            if line2=="":
                continue
            if line2.startswith("@"):
                #found instruction
                if line2.startswith("@prepend"):
                    arg=line2.replace("@prepend","").strip()
                    arg=arg.replace("$name",self.name)
                    self.prepend=arg.strip().strip(".")
                if line2.startswith("@template"):
                    arg=line2.replace("@template","").strip()
                    ddir=j.system.fs.getDirName(self.path)
                    for tpath in [arg,arg+".hrdt","%s/%s"%(ddir,arg),"%s/%s.hrdt"%(ddir,arg)]:
                        if j.system.fs.exists(path=tpath):
                            self.template=tpath

        for line in content.split("\n"):
            line2=line.strip()
            
            if line2=="":
                if state=="multiline":
                    #end of multiline var needs to be processed
                    state="var"
                else:
                    continue

            if line2.startswith("@"):
                continue

            if state=="multiline":
                if line[0]<>" ":
                    #end of multiline var needs to be processed
                    state="var"

            #look for comments at start of content
            if state=="start":
                if line[0]=="#":
                    self.commentblock+="%s\n"%line
                    continue
                else:
                    state="look4var"

            if state=="look4var":
                # print "%s:%s"%(state,line)
                if line.find("=")<>-1:
                    if line.find("#")<>-1:
                        line,comment0=line.split("#",1)
                        line2=line.strip()
                        comments+="#%s\n"%comment0
                    pre,post=line2.split("=",1)
                    vartype="unknown"
                    name=pre.strip()
                    if post.strip()=="" or post.strip().lower()=="@ask":
                        state="multiline"
                        if  post.strip().lower()=="@ask":
                            vartype="ask"                            
                        post=post.strip()+" " #make sure there is space trailing
                        continue
                    else:
                        vartype=self._recognizeType(post)
                        post=post.strip()
                        state="var"

                if line[0]=="#":
                    comments+="%s\n"%line

            if state=="multiline":                             
                if vartype=="unknown":
                    #means first line of multiline, this will define type
                    if line2.find(":")<>-1 and line2[-1]==",":
                        vartype="dict"
                    elif line2[-1]==",":
                        vartype="list"
                    else:
                        vartype="base" #newline text

                if vartype=="unknown":
                    raise RuntimeError("parse error, only dict, list, normal or ask format in multiline")

                if vartype=="base":
                    post+="%s\\n"%line2
                elif vartype=="dict" or vartype=="list":
                    post+="%s "%line2
                elif vartype=="ask":
                    post+="%s "%line2

            if state=="var":
                #now we have 1 liners and we know type
                if vartype=="ask":
                    vartype="base" #ask was temporary type, is really a string
                if self.prepend<>"":
                    name="%s.%s"%(self.prepend,name)
                self.items[name]=HRDItem(name,self,vartype,post,comments)
                if self.tree<>None:
                    self.tree.items[name]=self.items[name]
                    
                state="look4var"
                comments=""
                vartype="unknown"

        self.applytemplate()

    def processall(self):
        for key,hrditem in self.items.iteritems():
            hrditem._process()

    def pop(self,key):
        if self.has_key(key):
            self.items.pop(key)

    def has_key(self, key):
        return self.items.has_key(key)

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

    # def setDict(self,dictObject):
    #     self.items.update(dictObject)


    def __repr__(self):
        parts=[]
        keys=self.items.keys()
        keys.sort()
        if self.commentblock<>"":
            out=self.commentblock+"\n"
        else:
            out=""
        for key in keys:
            hrditem=self.items[key]            
            if hrditem.comments<>"":
                out+="\n%s\n" % (hrditem.comments.strip())
            out+="%s = %s\n" % (key, hrditem.getValOrDataAsStr())
        return out

    def __str__(self):
        return self.__repr__()


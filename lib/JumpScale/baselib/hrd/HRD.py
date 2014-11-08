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
        self.value=data
        self.comments=comments
        self._process()

    def _process(self):
        self.value=j.tools.text.ask(self.value)
        self.value=j.tools.text.hrd2machinetext(self.value)
        if self.ttype=="dict":
            currentobj={}
            for item in self.value.split(","):
                try:
                    key,post2=item.split(":",1)                                    
                except:
                    print self.hrd.content
                    from IPython import embed
                    print "DEBUG NOW HRDItem"
                    embed()
                    
                currentobj[key.strip()]=post2.strip()
            self.value=j.tools.text.str2var(currentobj)
        elif self.ttype=="list":
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
        self.tree=tree
        self.changed=False
        self.items={}
        self.commentblock=""  #at top of file

        if content<>"":
            self.process(content)
        else:
            self.read()

    def _markChanged(self):
        self.changed=True
        if self.tree<>None:
            self.tree.changed=True

    def set(self,key,value,persistent=True):
        """
        """
        key=key.lower()
        value=j.tools.text.pythonObjToStr(value)
        self.items[key]=value
        self.tree.items[key]=self
        if persistent:
            self.save()

    def save(self):
        
        if persistent==True:
            value=self._serialize(value)
            j.core.hrd.log("set in hrd:%s '%s':'%s'"%(self.path,key,value),category="set")

            if self.path=="" or not j.system.fs.exists(path=self.path):
                j.events.inputerror_critical("Cannot find hrd on %s"%self.path)

            out=""
            comment="" 
            keyfound = False
            for line in j.system.fs.fileGetContents(self.path).split("\n"):
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
            j.system.fs.writeFile(self.path,out)

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
        val= self.items[key]
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
        for key in self.prefix(prefix):
            result.append(self.get(key))
        return result
  
    def getDictFromPrefix(self, prefix):
        """
        returns values from prefix return as list
        """
        result={}
        for key in self.prefix(prefix):
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
        if content.find(":")<>-1:
            return "dict"
        elif content.find(",")<>-1:
            return "list"
        elif content.lower().strip().startswith("@ask"):
            return "ask"
        else:
            return "base"

    def process(self,content):

        if content=="":
            content=j.system.fs.fileGetContents(self.path)        

        state="start"
        comments=""
        multiline=""
        self.content=content

        for line in content.split("\n"):
            line2=line.strip()
            
            if line2=="":
                if state=="multiline":
                    #end of multiline var needs to be processed
                    state="var"
                else:
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
                    post+="%s, "%line2
                elif vartype=="ask":
                    post+="%s "%line2

            if state=="var":
                #now we have 1 liners and we know type
                if vartype=="ask":
                    vartype="base" #ask was temporary type, is really a string 
                self.items[name]=HRDItem(name,self,vartype,post,comments)
                    
                state="look4var"
                comments=""
                vartype="unknown"

        if content.find("prefix2.deeper.list")<>-1:
            from IPython import embed
            print "DEBUG NOW yuyuyuyu"
            embed()
 

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
        from IPython import embed
        print "DEBUG NOW uuu"
        embed()
        
        parts=[]
        keys=self.items.keys()
        keys.sort()
        if self.commentblock<>"":
            out=self.commentblock+"\n"
        else:
            out=""
        for key in keys:
            value=self.get(key)
            if self.comments.has_key(key):
                out+="\n%s\n" % (self.comments[key].strip())
            out+="%s = %s\n" % (key, j.tools.text.pythonObjToStr(value))
        return out

    def __str__(self):
        return self.__repr__()


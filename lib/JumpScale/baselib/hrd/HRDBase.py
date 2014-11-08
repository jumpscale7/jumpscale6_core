from JumpScale import j

class HRDBase():

    def set(self,key,value,persistent=True,comments=""):
        """
        """
        key=key.lower()
        if not self.items.has_key(key):
            self.items[key]=HRDItem(name=key,hrd=self,ttype="base",data=value,comments="")    
        self.items[key].set(value,persistent=persistent,comments=comments)

    def prefix(self, key):
        result=[]
        for knownkey in self.items.keys():
            # print "prefix: %s - %s"%(knownkey,key)
            if knownkey.startswith(key):
                result.append(knownkey)
        result.sort()                
        return result



    def getBool(self,key,default=None):
        res=self.get(key,default=default)
        if res==None:
            return False
        if res==True or res=="1" or res.lower()=="true":
            return True
        else:
            return False            

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

    def checkValidity(self,template,hrddata={}):
        """
        @param template is example hrd content block, which will be used to check against, 
        if params not found will be added to existing hrd 
        """      

        hrdtemplate=HRD(content=template)
        for key in hrdtemplate.items.keys():
            if not self.items.has_key(key):
                hrdtemplateitem=hrdtemplate.items[key]
                if hrddata.has_key(key):
                    data=hrddata[key]
                else:
                    data=hrdtemplateitem.data
                self.set(hrdtemplateitem.name,data,comments=hrdtemplateitem.comments)

    def processall(self):
        for key,hrditem in self.items.iteritems():
            hrditem._process()

    def pop(self,key):
        if self.has_key(key):
            self.items.pop(key)

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
        j.core.hrd.log("replace vars in hrd:%s"%hrdtree.path,"replacevar",7)
        if len(items)>0:
            for item in items:
                # print "look for : %s"%item
                item2=item.strip(" ").strip("$").strip(" ").strip("(").strip(")")

                if additionalArgs.has_key(item2.lower()):
                    newcontent=additionalArgs[item2.lower()]
                    content=content.replace(item,newcontent)
                else:
                    if self.exists(item2):
                        content=content.replace(item,self.getStr1Line(item2))                
        return content          

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


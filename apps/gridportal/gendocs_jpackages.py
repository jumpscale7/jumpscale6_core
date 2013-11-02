from JumpScale import j

j.application.start("gendocs")


outpath="jpackagedocs"

class JPdata():
    def __init__(self):
        self.domains={}

    def addDomain(self,ql,domain):
        self.domains[domain]=Domain(ql,domain)

    def addJPackage(self,ql,domain,packagename,version,path):
        if not self.domains.has_key(domain):
            self.addDomain(ql,domain)
        domaino=self.domains[domain]
        return domaino.addJPackage(ql,domain,packagename,version,path)

    def walk(self,method,params={}):
        keys=self.domains.keys()
        keys.sort()
        for dom in keys:
            domain=self.domains[dom]
            keys2=domain.packages.keys()
            keys2.sort()
            for name in keys2:
                jp=domain.packages[name]
                params=method(jp,params)
        return params

    def getPackageFromKey(self,key):
        for domname in self.domains.keys():
            domain=self.domains[domname]            
            if domain.packages.has_key(key):
                return domain.packages[key]
        raise RuntimeError("Cannot find package: %s"%key)

    def writeHrdList(self,path):

        params={}
        def hrdlist(jp,params):
            for hrdparam in jp.hrdvars.keys():
                jpkey,path=jp.hrdvars[hrdparam]
                params[hrdparam]=(jpkey,path)
            return params
        params=data.walk(hrdlist,params)
        self.hrdlist=params

        keys=self.hrdlist.keys()
        keys.sort()

        hrdPerJpackage={}
        for hrdkey in keys:
            jpkey,hrdpath=self.hrdlist[hrdkey]
            jp=self.getPackageFromKey(jpkey)
            if not hrdPerJpackage.has_key(jpkey):
                hrdPerJpackage[jpkey]=[]
            hrdPerJpackage[jpkey].append((hrdkey,hrdpath))

        jpkeys=hrdPerJpackage.keys()
        jpkeys.sort()
        out="h2. list of hrd keys\n\n"
        for jpkey in jpkeys:
            jp=self.getPackageFromKey(jpkey)
            out+="h3. %s\n"%jp.getKeyTitle()
            out+="* jpackage:[%s]\n"%jp.getKey()
            out+="* path:%s\n"%jp.path
            out+="||hrdkey||system val||hrd path||\n"
            for hrdkey,hrdpath in hrdPerJpackage[jpkey]:
                out+="|%s|$(%s)|%s|\n"%(hrdkey,hrdkey,hrdpath)
            out+="\n"
        path=j.system.fs.joinPaths(path,"hrdlist.wiki")
        j.system.fs.writeFile(path,out)

    def __repr__(self):
        out=""
        keys=self.domains.keys()
        keys.sort()
        for item in keys:
            out+="domain:%s\n%s\n\n"%(item,self.domains[item])
        return out

    __str__=__repr__


class Domain():
    def __init__(self,ql,name):
        self.ql=ql
        self.name=name
        self.packages={}

    def addJPackage(self,ql,domain,packagename,version,path):
        jp=JPackage(ql,domain,packagename,version,path)
        key=jp.getKey()
        if self.packages.has_key(key):
            prevjp=self.packages[key]
            newer=False
            from IPython import embed
            print "DEBUG NOW check previous jpackage, only when newer put"
            embed()
            if newer==False:
                return prevjp
            
        self.packages[key]=jp
        return jp

    def __repr__(self):
        out=""
        keys=self.packages.keys()
        keys.sort()
        for item in keys:
            out+="      %s\n"%(self.packages[item])
        return out

    __str__=__repr__


class JPackage():
    def __init__(self,ql,domain,packagename,version,path):
        self.ql=ql
        self.domain=domain
        self.name=packagename
        self.version=version
        self.path=path
        self.hrdvars={}

    def getKey(self):
        return "%s_%s_%s"%(self.name,self.domain,self.version)

    def getKeyTitle(self):
        return "%s %s (%s)"%(self.name,self.domain,self.version)

    def getHrdDoc(self,name):
        content,path=self.getHrdContent(name)
        out2 ="h2. %s\n\n"%self.getKeyTitle()
        out2 +="h3. %s\n"%name
        out2 +="* path:%s\n"%path
        out2 +="{{code:\n%s\n}}\n\n"%content
        return out2

    def listActiveHrd(self):
        content=j.system.fs.fileGetContents(hrdfile)
        path="%s/%s"%(self.path,"hrdactive")
        if not j.system.fs.exists(path):
            j.system.fs.createDir(path)
            j.system.fs.writeFile("%s/.empty"%path,".")
            
        hrdfiles=j.system.fs.listFilesInDir(path,True,"*.hrd")
        hrdfiles=[item for item in hrdfiles if j.system.fs.getBaseName(item)[0]<>"_"]
        result={}
        for item in hrdfiles:
            result[j.system.fs.getBaseName(item)]=item
        return result

    def getHrdContent(self,name):
        path=self.listActiveHrd()[name]
        content=j.system.fs.fileGetContents(path)
        for line in content.split("\n"):
            line=line.strip()
            if line=="" or line.find("=")==-1:
                continue
            name=line.split("=")[0]
            name=name.strip()
            self.hrdvars[name]=(self.getKey(),path)
        return content,path

    def getDocPath(self,path,name=""):
        if name=="":
            path=j.system.fs.joinPaths(path,self.ql,self.domain,self.name,"%s.wiki"%self.name)        
        else:
            path=j.system.fs.joinPaths(path,self.ql,self.domain,self.name,"%s.wiki"%name)        
        j.system.fs.createDir(j.system.fs.getDirName(path))
        return path

    def writeHrdDoc(self,path):
        out=""
        for name in self.listActiveHrd().keys():
            out+=self.getHrdDoc(name)
        if out<>"":
            path=self.getDocPath(path,"activehrd_%s"%name)
            j.system.fs.writeFile(path,out)

    def __repr__(self):
        out="%s"%self.getKeyTitle()
        return out

    __str__=__repr__


data=JPdata()

jpackagedirs=[item for item in j.system.fs.listDirsInDir("/opt/code",recursive=True) if j.system.fs.getBaseName(item).find("jp_")==0]
for jpackagedir in jpackagedirs:
    hrdfiles=j.system.fs.listFilesInDir(jpackagedir,True,"main.hrd")
    for hrdfile in hrdfiles:
        ql=j.system.fs.getDirName(hrdfile,levelsUp=3)
        if ql=="unstable":
            domain=j.system.fs.getDirName(hrdfile,levelsUp=4)
            packagename=j.system.fs.getDirName(hrdfile,levelsUp=2)
            version=j.system.fs.getDirName(hrdfile,levelsUp=1)
            path=j.system.fs.getParent(hrdfile)
            path=j.system.fs.getParent(path)
            jp=data.addJPackage(ql,domain,packagename,version,path)
            print jp.getKeyTitle()
            jp.writeHrdDoc(outpath)

data.writeHrdList(outpath)


from IPython import embed
print "DEBUG NOW main"
embed()


j.application.stop()

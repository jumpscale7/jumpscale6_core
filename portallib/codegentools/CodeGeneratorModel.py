from OpenWizzy import o

from CodeGeneratorBase import CodeGeneratorBase

class CodeGeneratorModel(CodeGeneratorBase):
    def __init__(self,spec,typecheck=True,dieInGenCode=True,codepath="",writeForm=True):
        self.codepath=codepath
        self._writeForm = writeForm
        CodeGeneratorBase.__init__(self,spec,typecheck,dieInGenCode)
        self.type="pymodel"        
        # self.initprops+="        self._appname=\"%s\"\n" %spec.appname
        # self.initprops+="        self._actorname=\"%s\"\n" %spec.actorname
        # self.initprops+="        self._modelname=\"%s\"\n" %spec.name

    def getPropertyCode(self,name,type,indent=1):
        value=""
        pre=""
        init=""
        typemap = {'bool': 'boolean','str': 'string', 'dict': 'dictionary', 'int': 'integer'}
        defaultmap = {'int': '0', 'str': '""', 'float': '0.0', 'bool': 'True', 'list': 'list()', 'dict': 'dict()' }
        if '(' in type:
            type = type[0:type.index('(')]

        s = """
if not isinstance(value, %(type)s) and value is not None:
    if isinstance(value, basestring) and o.basetype.%(fulltype)s.checkString(value):
        value = o.basetype.%(fulltype)s.fromString(value)
    else:
        msg="property %(name)s input error, needs to be %(type)s, specfile: %(specfile)s, name model: %(modelname)s, value was:" + str(value)
        raise RuntimeError(msg)
""" % {'name': name, 'fulltype': typemap.get(type, type),'type': type, 
       'specfile': self.spec.specpath.replace("\\", "/"), 'modelname': self.spec.name}

        if type in defaultmap:
            init = "self._P_%s=%s" % (name, defaultmap.get(type))
        else:
            specfound=o.core.specparser.findSpec(query=type,findFromSpec=self.spec)

            if specfound.type=="enumeration":
                init="self._P_%s=0" % name #is the unknown type
                o.core.codegenerator.generate(specfound,type="enumerator")
                name,path=o.core.codegenerator.getCodeId(specfound,type="enumerator")
                if not o.core.codegenerator.classes.has_key(name):
                    raise RuntimeError("generation was not successfull for %s, there should be a classes populated" %name)
                enumerationcheck="o.enumerators.%s" % name.split("enumeration_")[1]
                s="%s.check(value) or isinstance(value, int)"%enumerationcheck
                type="enumerator:%s or int" % type
                value="int(value)"
            elif specfound.type=="model":
                pre="classs=o.core.codegenerator.getClassPymodel(\"%s\",\"%s\",\"%s\")\n" %(specfound.appname,specfound.actorname,specfound.name)
                s="isinstance(value, classs)"
                init=pre
                init+="self._P_%s=classs()" % name
            else:
                s=""
        s = o.code.indent(s, indent)
        self.initprops+=o.code.indent(init,2)
        return s,value



    def addProperty(self,propertyname,type,default,description):

        s="""
    @property
    def {name}(self):
        return self._P_{name}
    @{name}.setter
    def {name}(self, value):
{optionalvalidation}
        self._P_{name}={value}
    @{name}.deleter
    def {name}(self):
        del self._P_{name}

"""
        s=s.replace("{name}",propertyname)
        validation,value=self.getPropertyCode(propertyname,type,2)
        if value=="":
            value="value"
        s=s.replace("{optionalvalidation}",validation)
        s=s.replace("{value}",value)
        self.content+=s

    def addNewObjectMethod(self,propname,rtype,spec):
        if propname[-1]=="s":
            propname2=propname[:-1]
        else:
            propname2=propname
        if rtype=="list":
            s="def new_%s(self,value=None):\n" % propname2
        else:
            s="def new_%s(self,key,value=None):\n" % propname2
        self.content+="\n%s"%o.code.indent(s,1)
        s=""

        if spec not in  ["int","bool","float","str","list","dict"]:
            classstr="o.core.codegenerator.getClassPymodel(\"%s\",\"%s\",\"%s\")()" %(spec.appname,spec.actorname,spec.name)
        else:
            if spec=="int":
                classstr="0"
            elif spec=="bool":
                classstr="False"
            elif spec=="float":
                classstr="0.0"
            elif spec=="str":
                classstr="\"\""
            elif spec=="list":
                classstr="[]"
            elif spec=="dict":
                classstr="{}"

        s+="if value==None:\n"
        s+="    value2=%s\n" %classstr
        s+="else:\n"
        s+="    value2=value\n"

        if rtype=="list":
            ssss="""
self._P_{name}.append(value2)
if self._P_{name}[-1].__dict__.has_key("_P_id"):
    self._P_{name}[-1].id=len(self._P_{name})
return self._P_{name}[-1]\n
"""
            ssss=ssss.replace("{name}",propname)
            s+=ssss
        else:
            s+="self._P_%s[key]=value2\n" % propname
            s+="return self._P_%s[key]\n" % propname


        self.content+="\n%s"%o.code.indent(s,2)


    def getModelFormMacroContent(self):

        C="""
def main(o,args,params,tags,tasklet):
    
    page=args.page

    mod=q.html.getPageModifierBootstrapForm(page)

    appname="{appname}"
    actorname="{actor}"
    modelname="{modelname}"

    if not args.paramsExtra.has_key("guid"):
        raise RuntimeError("ERROR: guid was not known when requesting this page, needs to be an arg")
    guid=args.paramsExtra["guid"]

    actor=o.apps.{appname}.{actor}
    model=actor.models.{modelname}.get(guid=guid)

    form=mod.getForm("{modelname}",actor)

{formbuild}

    params.result=mod.addForm(form)    

    return params


def match(o,args,params,tags,tasklet):
    return True

"""        
        C=C.replace("{modelname}",self.spec.name)
        C=C.replace("{appname}",self.spec.appname)
        C=C.replace("{actor}",self.spec.actorname)

        modelspec=o.core.specparser.getModelSpec(self.spec.appname,self.spec.actorname,self.spec.name) 

        C2=""

        for prop in modelspec.properties:
            if prop.name<>"guid":
                C3="""    form.addTextInput("$name",reference=form.getReference(model,"$name"),default="$default",help="")\n"""
                C3=C3.replace("$name",prop.name)
                if prop.default==None:
                    default=""
                else:
                    default=str(prop.default)
                C3=C3.replace("$default",default)
                C2+=C3

        C=C.replace("{formbuild}",C2)

        return C



    def writeForm(self): #@todo will have to be moved to other generator because now this generator cannot be used client side

        ppath=o.system.fs.joinPaths(self.codepath,"space_%s__%s"%(self.spec.appname,self.spec.actorname))

        ppath3=o.system.fs.joinPaths(ppath,"form_%s"%(self.spec.name))
        if not o.system.fs.exists(ppath3):
            o.system.fs.createDir(ppath3)        

            C="""
h2. {modelname}

{{form_{actor}_{modelname}}}

"""        
            C=C.replace("{modelname}",self.spec.name)
            C=C.replace("{actor}",self.spec.actorname)

            ppath2=o.system.fs.joinPaths(ppath3,"form_%s.wiki"%(self.spec.name))
            o.system.fs.writeFile(ppath2,C)

        #create macro
        ppath3=o.system.fs.joinPaths(ppath,".macros","page","form_%s_%s"%(self.spec.actorname,self.spec.name))
        if True or not o.system.fs.exists(ppath3): #@todo despiegk loader
            o.system.fs.createDir(ppath3)        

            ppath2=o.system.fs.joinPaths(ppath3,"5_form_%s_%s.py"%(self.spec.actorname,self.spec.name))
            o.system.fs.writeFile(ppath2,self.getModelFormMacroContent())

    def addInitExtras(self):
        # following code will be loaded at runtime
        s="""
self._P__meta=["{appname}","{actorname}","{modelname}",{version}] #@todo version not implemented now, just already foreseen
"""
        s=s.replace("{appname}",self.spec.appname)
        s=s.replace("{actorname}",self.spec.actorname)
        s=s.replace("{modelname}",self.spec.name)
        s=s.replace("{version}","1")
        self.initprops+=o.code.indent(s,2)


    def generate(self):
        self.addClass(baseclass="o.code.classGetPyModelBase()")

        for prop in self.spec.properties:
            self.addProperty( propertyname=prop.name, type=prop.type, default=prop.default, description=prop.description)

        if "guid" not in [item.name for item in self.spec.properties]:
            self.addProperty( propertyname="guid", type="str", default="", description="unique guid for object")

        self.addProperty( propertyname="_meta", type="list", default=[], description="metainfo")

        #if "id" not in [item.name for item in self.spec.properties]:
            #self.addProperty( propertyname="id", type="int", default="", description="unique id for object")

        for prop in self.spec.properties:

                rtype,spec=o.core.specparser.getSpecFromTypeStr(self.spec.appname,self.spec.actorname,prop.type)
                #print str(rtype)+" : "+str(spec)
                if rtype<>None and rtype<>"object" and rtype<>"enum":
                    if spec not in ["int","bool","float","str"]:
                        self.addNewObjectMethod(prop.name,rtype,spec)


        self.addInitExtras()
        if self._writeForm:
            self.writeForm()

        return self.getContent()





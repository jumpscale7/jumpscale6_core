from OpenWizzy import o
import traceback
 
class MacroExecutorBase():


    def getMacroCandidates(self,txt):
        result=[]
        items=txt.split("{{")
        for item in items:
            if item.find("}}")<>-1:
                item=item.split("}}")[0]
                if item not in result:
                    result.append("{{%s}}"%item)
        return result

    def parseMacroStr(self,macrostr):
        """
        @param macrostr full string like {{test something more}}
        @return macroname,openwizzytags
        """
        cmdstr=macrostr.replace("{{","").replace("}}","").strip()
        if cmdstr.find("\n")<>-1:
            #multiline
            cmdbody="\n".join(cmdstr.split("\n")[1:])
            cmdstr=cmdstr.split("\n")[0]
        else:
            cmdbody=""
        if cmdstr.find(" ")>cmdstr.find(":") or (cmdstr.find(" ")==-1 and cmdstr.find(":")<>-1):
            macro=cmdstr.split(":")[0].lower()
        elif cmdstr.find(" ")<cmdstr.find(":") or (cmdstr.find(":")==-1 and cmdstr.find(" ")<>-1):
            macro=cmdstr.split(" ")[0].lower()
        else:
            macro=cmdstr.lower()
        
        tags=o.core.tags.getObject(cmdstr)
            
        if cmdstr.strip().find(macro)==0:
            cmdstr=cmdstr.strip()[len(macro):]
            while len(cmdstr)>0 and (cmdstr[0]==" " or cmdstr[0]==":") :
                cmdstr=cmdstr[1:]
        
        if cmdbody<>"":
            cmdstr=cmdbody            

        return macro,tags,cmdstr

    def findMacros(self,text):
        """
        @returns list of list with macrostrwithtags,withouttags
        """
        if text.strip()=="":
            return []
        return self.getMacroCandidates(text)



class MacroExecutorPreprocess(MacroExecutorBase):
    def __init__(self,macrodirs=[]):
        self.taskletsgroup=o.core.taskletengine.getGroup(o.tools.docpreprocessor.getMacroPath())
        self.priority={}
        for macrodir in macrodirs:
            self.taskletsgroup.addTasklets(macrodir)

            macrosprocessed={}

            self.priority[8]=[]

            cfg=o.system.fs.joinPaths(macrodir,"prio.cfg")
            if o.system.fs.exists(cfg):
                lines=o.system.fs.fileGetContents(cfg).split("\n")
                for line in lines:
                    prio,macroname=line.split(":")
                    macroname=macroname.lower().strip()
                    prio=int(prio)
                    if not self.priority.has_key(prio):
                        self.priority[prio]=[]
                    self.priority[prio].append(macroname)
                    macrosprocessed[macroname]=True

            for name in self.taskletsgroup.taskletEngines.keys():
                if not macrosprocessed.has_key(name):
                    self.priority[8].append(name)



    def _executeMacroOnDoc(self,macrostr,doc,paramsExtra=None):
        """
        find macro's in a doc & execute the macro
        a doc is a document in preprocessor phase
        """
        macro,tags,cmdstr=self.parseMacroStr(macrostr)
        if not paramsExtra:
            paramsExtra = {}
        if self.taskletsgroup.hasGroup(macro):
            result,doc=self.taskletsgroup.executeV2(macro,doc=doc,tags=tags,macro=macro,macrostr=macrostr,paramsExtra=paramsExtra,cmdstr=cmdstr)
            if result<>None:
                if not o.basetype.string.check(result):
                    result="***ERROR***: Could not execute macro %s on %s, did not return content as string (params.result=astring)" % (macro,doc.name)
                doc.content=doc.content.replace(macrostr,result)    
        return doc


    def execMacrosOnDoc(self,doc,paramsExtra={}):

        macrostrs=self.findMacros(doc.content)
        if len(macrostrs)>0:
            macros={}
            for macrostr in macrostrs:
                macro,tags,cmdstr=self.parseMacroStr(macrostr)
                macro=macro.lower().strip()
                if not macros.has_key(macro):
                    macros[macro]=[]
                #check which macro's are params
                if paramsExtra.has_key(macro):
                    doc.content=doc.content.replace(macrostr,paramsExtra[macro])
                    continue
                if doc.preprocessor.params.has_key(macro):
                    doc.content=doc.content.replace(macrostr,self.params[macro])
                    continue
                if macro=="author":
                    doc.content=doc.content.replace(macrostr,','.join(doc.author))
                    continue
                if macro=="docpathshort":
                    doc.content=doc.content.replace(macrostr,doc.shortpath)
                    continue
                if macro=="docpath":
                    doc.content=doc.content.replace(macrostr,doc.path)
                    continue

                macros[macro].append([macrostr,tags])

            for prio in range(0,10):
                if self.priority.has_key(prio):
                    for macro in self.priority[prio]:
                        if macros.has_key(macro):
                            #found macrow which is in doc sorted following priority
                            for macrostr,tags in macros[macro]:
                                doc=self._executeMacroOnDoc(macrostr,doc)
        return doc


class MacroExecutorPage(MacroExecutorBase):
    def __init__(self,macrodirs=[]):
        self.taskletsgroup=o.core.taskletengine.getGroup(o.tools.docgenerator.getMacroPath())
        for macrodir in macrodirs:
            self.taskletsgroup.addTasklets(macrodir)
        self.taskletsgroup2=None


    def executeMacroAdd2Page(self,macrostr,page,doc=None,requestContext=None,paramsExtra=""):
        """
        @param macrostr full string like {{test something more}}
        @param page is htmlpage, rstpage, confluencepage, ...
        find macro's in a page & execute the macro
        a doc is a document in final phase whichere the final result is generated
        """     

        if not str(type(page))=="<type 'instance'>" or not page.__dict__.has_key("body"):            
            raise RuntimeError("Page was no page object. Was for macro:%s on doc:%s"%(macrostr,doc.name))

        macro,tags,cmdstr=self.parseMacroStr(macrostr)

        #print "execute macro %s on page %s" % (macrostr,page.name)
        #for ease of use add the requestContext params to the main params

        if self.taskletsgroup2<>None and self.taskletsgroup2.hasGroup(macro):
            page=self.taskletsgroup2.executeV2(macro,doc=doc,tags=tags,macro=macro,macrostr=macrostr,\
                paramsExtra=paramsExtra,cmdstr=cmdstr,page=page,requestContext=requestContext)
        elif self.taskletsgroup.hasGroup(macro):
            page=self.taskletsgroup.executeV2(macro,doc=doc,tags=tags,macro=macro,macrostr=macrostr,\
                paramsExtra=paramsExtra,cmdstr=cmdstr,page=page,requestContext=requestContext)
        else:
            page.addMessage("***error***: could not find macro %s" % macro)

        if not str(type(page))=="<type 'instance'>" or not page.__dict__.has_key("body"):
            raise RuntimeError("params.page object which came back from macro's does not represent a page. Was for macro:%s on doc:%s"%(macro,doc.name))

        page.body=page.body.replace("\{","{")

        return page

    def executeMacroReturnHTML(self,macrostr,doc=None,requestContext=None,paramsExtra="",pagemirror4jscss=None):
        """
        macrostr is already formatted like {{....}} and only that is returned, 
        use executeMacrosInWikiContent instead to process macros in a full text
        """
        page0=o.core.appserver6.runningAppserver.webserver.getpage()
        if pagemirror4jscss<>None:
            page0.pagemirror4jscss=pagemirror4jscss
        page0=self.executeMacroAdd2Page(macrostr,page0,doc,requestContext,paramsExtra)
        return page0.body

    def  processMacrosInWikiContent(self,content):
        for macrostr,macrocmd in self.findMacros(content):
            print "DEBUG NOW macro in wiki  content (e.g. for table)"
            from IPython import embed
            embed()
        return content
            


class MacroExecutorWiki(MacroExecutorBase):
    def __init__(self,macrodirs):
        if len(macrodirs)==0:
            raise RuntimeError("need to specify a macrodir, cannot be empty")
        self.taskletsgroup=o.core.taskletengine.getGroup(macrodirs.pop())
        for macrodir in macrodirs:
            self.taskletsgroup.addTasklets(macrodir)

    def execMacrosOnContent(self,content,doc,paramsExtra={},recursivedepth=0,ctx=None):
        recursivedepth+=1
        if ctx<>None:
            content=doc.applyParams(ctx.params,findfresh=True,content=content)
        if paramsExtra<>{}:
            content=doc.applyParams(paramsExtra,findfresh=True,content=content)
        macrostrs=self.findMacros(content)
        for macrostr in macrostrs:
            #print "EXEC MACRO ONCONTENT:"
            #print macrostr
            #print recursivedepth
            if recursivedepth>20:
                content+='ERROR: recursive error in executing macro %s' % macrostr
                return
            content,doc=self.executeMacroOnContent(content,macrostr,doc,paramsExtra,ctx=ctx)
            content,doc=self.execMacrosOnContent(content,doc,paramsExtra,recursivedepth,ctx=ctx) #work recursive see if other macro's
        return content,doc

    def executeMacroOnContent(self,content,macrostr,doc,paramsExtra=None,ctx=None):
        """
        find macro's in a doc & execute the macro
        a doc is a document in preprocessor phase
        """
        macro,tags,cmdstr=self.parseMacroStr(macrostr)
        if self.taskletsgroup.hasGroup(macro):
            try:
                result,doc=self.taskletsgroup.executeV2(groupname=macro,doc=doc,tags=tags,macro=macro,macrostr=macrostr,\
                    paramsExtra=paramsExtra,cmdstr=cmdstr,requestContext=ctx)
            except Exception:
                e = traceback.format_exc()
                if str(e).find("non-sequence")<>-1:
                    result="***ERROR***: Could not execute macro %s on %s, did not return (out,doc)." % (macro,doc.name)                    
                else:
                    result="***ERROR***: Could not execute macro %s on %s, error in macro. Error was:\n%s " % (macro,doc.name,e)
            if result<>None:
                if not o.basetype.string.check(result):
                    result="***ERROR***: Could not execute macro %s on %s, did not return content as string (params.result=astring)" % (macro,doc.name)
                content=content.replace(macrostr,result)
        else:
            content=content.replace(macrostr,"***ERROR***: Could not execute macro %s on %s, did not find the macro, was a wiki macro." % (macro,doc.name))
        return content,doc


    def findMacros(self,text):
        """
        """
        if text.strip()=="":
            return []
        #result=o.codetools.regex.findAll("\{\{[\w :;,\.\*\!\?\^\=\'\-/]*\}\}",text) #finds {{...}}
        #result=o.codetools.regex.findAll("(?s)\{\{.*\}\}",text) #finds {{...}}
        #result2=[[item,item.replace("{{","").replace("}}","").strip()] for item in result]
        result3=[]
        #print self.getMacroCandidates(text)
        #print "*************"
        for item in self.getMacroCandidates(text): #make unique
            macro,tags,cmd=self.parseMacroStr(item)
            #print "macro2:%s" % macro
            if self.taskletsgroup.hasGroup(macro):
                result3.append(item)

        return result3


    def existsMacros(self,doc):
        macrostrs=self.findMacros(doc.content)
        for macrostr in macrostrs:
            macro,tags,cmd=self.parseMacroStr(macrostr)
            if self.taskletsgroup.hasGroup(macro):
                return True
        return False


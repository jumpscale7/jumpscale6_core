from JumpScale import j
import traceback


class MacroExecutorBase(object):
    def __init__(self, macrodirs=[]):
        self.taskletsgroup = dict()
        self.addMacros(macrodirs, None)

    def addMacros(self, macrodirs, spacename):
        spacename = spacename.lower() if spacename else None
        taskletsgroup = j.core.taskletengine.getGroup()
        for macrodir in macrodirs:
            taskletsgroup.addTasklets(macrodir)
        self.taskletsgroup[spacename] = taskletsgroup

    def getMacroCandidates(self, txt):
        result = []
        items = txt.split("{{")
        for item in items:
            if item.find("}}") != -1:
                item = item.split("}}")[0]
                if item not in result:
                    result.append("{{%s}}" % item)
        return result

    def _getTaskletGroup(self, doc, macrospace, macro):
        # if macrospace specified check there first
        spacename = doc.getSpaceName().lower()
        if macrospace is not None:
            macrospace = macrospace or None
            if macrospace:
                j.core.portal.active.spacesloader.spaces[macrospace].loadDocProcessor()
            if macrospace in self.taskletsgroup and self.taskletsgroup[macrospace].hasGroup(macro):
                return self.taskletsgroup[macrospace]
        # else check in document space
        if spacename in self.taskletsgroup and self.taskletsgroup[spacename].hasGroup(macro):
            return self.taskletsgroup[spacename]
        # last fall back to default macros
        if self.taskletsgroup[macrospace].hasGroup(macro):
            return self.taskletsgroup[macrospace]
        return None

    def parseMacroStr(self, macrostr):
        """
        @param macrostr full string like {{test something more}}
        @return macroname,jumpscaletags
        """
        cmdstr = macrostr.replace("{{", "").replace("}}", "").strip()
        if cmdstr.find("\n") != -1:
            # multiline
            cmdbody = "\n".join(cmdstr.split("\n")[1:])
            cmdstr = cmdstr.split("\n")[0]
        else:
            cmdbody = ""
        if cmdstr.find(" ") > cmdstr.find(":") or (cmdstr.find(" ") == -1 and cmdstr.find(":") != -1):
            macro = cmdstr.split(":")[0].lower()
        elif cmdstr.find(" ") < cmdstr.find(":") or (cmdstr.find(":") == -1 and cmdstr.find(" ") != -1):
            macro = cmdstr.split(" ")[0].lower()
        else:
            macro = cmdstr.lower()

        tags = j.core.tags.getObject(cmdstr)

        if cmdstr.strip().find(macro) == 0:
            cmdstr = cmdstr.strip()[len(macro):]
            while len(cmdstr) > 0 and (cmdstr[0] == " " or cmdstr[0] == ":"):
                cmdstr = cmdstr[1:]

        if cmdbody != "":
            cmdstr = cmdbody

        macroparts = macro.split('.', 1)
        if len(macroparts) == 2:
            space, macro  = macroparts
        else:
            space = None

        return space, macro, tags, cmdstr

    def findMacros(self, doc):
        """
        @returns list of list with macrostrwithtags,withouttags
        """
        text = doc.content.strip()
        if text == "":
            return []
        return self.getMacroCandidates(text)


class MacroExecutorPreprocess(MacroExecutorBase):

    def __init__(self, *args, **kwargs):
        self.priority = dict()
        super(MacroExecutorPreprocess, self).__init__(*args, **kwargs)

    def addMacros(self, macrodirs, spacename):
        taskletgroup = j.core.taskletengine.getGroup()
        self.taskletsgroup[spacename] = taskletgroup
        priority = dict()
        self.priority[spacename] = priority
        for macrodir in macrodirs:
            taskletgroup.addTasklets(macrodir)
            cfg = j.system.fs.joinPaths(macrodir, "prio.cfg")
            if j.system.fs.exists(cfg):
                lines = j.system.fs.fileGetContents(cfg).split("\n")
                for line in lines:
                    prio, macroname = line.split(":")
                    priority[macroname] = int(prio)

    def _executeMacroOnDoc(self, macrospace, macro, tags, cmdstr, macrostr, doc, paramsExtra=None):
        """
        find macro's in a doc & execute the macro
        a doc is a document in preprocessor phase
        """
        if not paramsExtra:
            paramsExtra = {}
        taskletgroup = self._getTaskletGroup(doc, macrospace, macro)
        if taskletgroup:
            result2 = taskletgroup.executeV2(macro, doc=doc, tags=tags, macro=macro, macrostr=macrostr, paramsExtra=paramsExtra, cmdstr=cmdstr)
            try:
                result, doc =result2
            except:
                taskletPath= taskletgroup.taskletEngines[macro].path
                raise RuntimeError("Cannot execute macro: %s on doc:%s, tasklet:%s, did not return (result,doc)."%(macrostr,taskletPath,doc))

            if result != None:
                if not j.basetype.string.check(result):
                    result = "***ERROR***: Could not execute macro %s on %s, did not return content as string (params.result=astring)" % (macro, doc.name)
                doc.content = doc.content.replace(macrostr, result)
        return doc

    def execMacrosOnDoc(self, doc, paramsExtra={}):
        spacename = doc.getSpaceName().lower()
        def macrosorter(entry):
            space = entry[0] or spacename
            return self.priority.get(space, dict()).get(entry[1], 9999)

        macrostrs = self.findMacros(doc)
        if len(macrostrs) > 0:
            macros = list()
            for macrostr in macrostrs:
                macrospace, macro, tags, cmdstr = self.parseMacroStr(macrostr)
                macro = macro.lower().strip()
                # check which macro's are params
                if macro in paramsExtra:
                    doc.content = doc.content.replace(macrostr, paramsExtra[macro])
                    continue
                if macro in doc.preprocessor.params:
                    doc.content = doc.content.replace(macrostr, self.params[macro])
                    continue
                if macro == "author":
                    doc.content = doc.content.replace(macrostr, ','.join(doc.author))
                    continue
                if macro == "docpathshort":
                    doc.content = doc.content.replace(macrostr, doc.shortpath)
                    continue
                if macro == "docpath":
                    doc.content = doc.content.replace(macrostr, doc.path)
                    continue
                macros.append((macrospace, macro, tags, cmdstr, macrostr, doc))

            for macroentry in sorted(macros, key=macrosorter):
                doc = self._executeMacroOnDoc(*macroentry)
        return doc


class MacroExecutorPage(MacroExecutorBase):

    def executeMacroAdd2Page(self, macrostr, page, doc=None, requestContext=None, paramsExtra=""):
        """
        @param macrostr full string like {{test something more}}
        @param page is htmlpage, rstpage, confluencepage, ...
        find macro's in a page & execute the macro
        a doc is a document in final phase whichere the final result is generated
        """

        if not str(type(page)) == "<type 'instance'>" or "body" not in page.__dict__:
            raise RuntimeError("Page was no page object. Was for macro:%s on doc:%s" % (macrostr, doc.name))

        macrospace, macro, tags, cmdstr = self.parseMacroStr(macrostr)

        # print "execute macro %s on page %s" % (macrostr,page.name)
        # for ease of use add the requestContext params to the main params
        taskletgroup = self._getTaskletGroup(doc, macrospace, macro)

        if taskletgroup:
            page = taskletgroup.executeV2(macro, doc=doc, tags=tags, macro=macro, macrostr=macrostr,
                                                 paramsExtra=paramsExtra, cmdstr=cmdstr, page=page, requestContext=requestContext)
        else:
            page.addMessage("***error***: could not find macro %s" % macro)

        if not str(type(page)) == "<type 'instance'>" or "body" not in page.__dict__:
            raise RuntimeError("params.page object which came back from macro's does not represent a page. Was for macro:%s on doc:%s" % (macro, doc.name))

        page.body = page.body.replace("\{", "{")

        return page

    def executeMacroReturnHTML(self, macrostr, doc=None, requestContext=None, paramsExtra="", pagemirror4jscss=None):
        """
        macrostr is already formatted like {{....}} and only that is returned, 
        use executeMacrosInWikiContent instead to process macros in a full text
        """
        page0 = j.core.portal.active.getpage()
        if pagemirror4jscss != None:
            page0.pagemirror4jscss = pagemirror4jscss
        page0 = self.executeMacroAdd2Page(macrostr, page0, doc, requestContext, paramsExtra)
        return page0.body

    def processMacrosInWikiContent(self, content):
        for macrostr, macrocmd in self.findMacros(content):
            print "DEBUG NOW macro in wiki  content (e.g. for table)"
            from IPython import embed
            embed()
        return content


class MacroExecutorWiki(MacroExecutorBase):

    def execMacrosOnContent(self, content, doc, paramsExtra={}, recursivedepth=0, ctx=None):
        recursivedepth += 1
        if ctx != None:
            content = doc.applyParams(ctx.params, findfresh=True, content=content)
        if paramsExtra != {}:
            content = doc.applyParams(paramsExtra, findfresh=True, content=content)
        macrostrs = self.findMacros(doc, content)
        for macrostr in macrostrs:
            # print "EXEC MACRO ONCONTENT:"
            # print macrostr
            # print recursivedepth
            if recursivedepth > 20:
                content += 'ERROR: recursive error in executing macro %s' % macrostr
                return content, doc
            content, doc = self.executeMacroOnContent(content, macrostr, doc, paramsExtra, ctx=ctx)
            #content, doc = self.execMacrosOnContent(content, doc, paramsExtra, recursivedepth, ctx=ctx)  # work recursive see if other macro's
        print 'ddddd'
        return content, doc

    def executeMacroOnContent(self, content, macrostr, doc, paramsExtra=None, ctx=None):
        """
        find macro's in a doc & execute the macro
        a doc is a document in preprocessor phase
        """
        macrospace, macro, tags, cmdstr = self.parseMacroStr(macrostr)
        taskletgroup = self._getTaskletGroup(doc, macrospace, macro)
        if taskletgroup:
            try:
                result, doc = taskletgroup.executeV2(groupname=macro, doc=doc, tags=tags, macro=macro, macrostr=macrostr,
                                                            paramsExtra=paramsExtra, cmdstr=cmdstr, requestContext=ctx, content=content)
            except Exception:
                e = traceback.format_exc()
                if str(e).find("non-sequence") != -1:
                    result = "***ERROR***: Could not execute macro %s on %s, did not return (out,doc)." % (macro, doc.name)
                else:
                    result = "***ERROR***: Could not execute macro %s on %s, error in macro. Error was:\n%s " % (macro, doc.name, e)
            if result == doc:
                # means we did manipulate the doc.content
                doc.content = doc.content.replace(macrostr, "")
                return doc.content, doc

            if result != None:
                if not j.basetype.string.check(result):
                    result = "***ERROR***: Could not execute macro %s on %s, did not return content as string (params.result=astring)" % (macro, doc.name)
                content = content.replace(macrostr, result)
        else:
             result="***ERROR***: Could not execute macro %s on %s, did not find the macro, was a wiki macro." % (macro, doc.name)

        content = content.replace(macrostr,result)

        return content,doc

    def findMacros(self, doc, content=None):
        """
        """
        content = content or doc.content
        text = content.strip()
        if text == "":
            return []
        result = []
        for item in self.getMacroCandidates(text):  # make unique
            macrospace, macro, tags, cmd = self.parseMacroStr(item)
            # print "macro2:%s" % macro
            if self._getTaskletGroup(doc, macrospace, macro):
                result.append(item)

        return result


    def existsMacros(self, doc):
        macrostrs = self.findMacros(doc)
        for macrostr in macrostrs:
            macrospace, macro, tags, cmd = self.parseMacroStr(macrostr)
            if not self._getTaskletGroup(doc, macrospace, macro):
                return False
        return False

from JumpScale import j


class DataTables():

    def __init__(self):
        self.inited = False
        self.cache = {}
        self.cacheg = {}

    def getActorModel(self, appname, actorname, modelname):
        try:
            actor = j.core.portal.runningPortal.actorsloader.getActor(appname, actorname)
            model = actor.models.__dict__[modelname]
        except Exception as e:
            # self.page.addMessage()
            raise RuntimeError("Error: could not find app with appname:%s, actorname:%s, model:%s" % (appname, actorname, modelname))
        return actor, model

    def getTableDefFromActorModel(self, appname, actorname, modelname, excludes=[]):
        """
        @return fields : array where int of each col shows position in the listProps e.g. [3,4] 
              means only col 3 & 4 from listprops are levant, you can also use it to define the order
              there can be special columns added which are wiki templates to form e.g. an url or call a macro, formatted as a string
              e.g. [3,4,"{{amacro: name:$3 descr:$4}}","[$1|$3]"]
        @return fieldids: ids to be used for the fields ["name","descr","remarks","link"]
        @return fieldnames: names to be used for the fields ["Name","Description","Remarks","Link"], can be manipulated for e.g. translation
        """
        actor, model = self.getActorModel(appname, actorname, modelname)
        excludes = [item.lower() for item in excludes]
        fields = []
        fieldids = []
        fieldnames = []
        counter = 0
        iddone = False

        def getGuidPos():
            if "guid" in model.listProps:
                pos = model.listProps.index("guid")
                return pos
            raise RuntimeError("Could not find position of guid in %s %s %s" % (appname, actorname, modelname))
        for prop in model.listProps:
            fprop = counter
            lprop = prop.lower().strip().replace(" ", "")
            if lprop not in excludes:
                # if lprop.find("id")==0 and iddone==False:
                #     fprop="[$%s|%s]"%(counter,"/%s/%s/view_%s?guid=$%s"%(appname,actorname,modelname,getGuidPos()))
                #     iddone=True
                # if lprop.find("name")<>-1 and iddone==False and guidpos<>None:
                #     fprop="[$%s|%s]"%(counter,"/%s/%s/view_%s?guid=$%s"%(appname,actorname,modelname,getGuidPos()))
                #     iddone=True
                fprop = "[$%s|%s]" % (counter, "/space_%s__%s/form_%s?guid=$%s" % (appname, actorname, modelname, getGuidPos()))
                iddone = True
                fields.append(fprop)
                fieldids.append(lprop)
                fieldnames.append(prop)
            counter += 1

        return actor, model, fields, fieldids, fieldnames

    def storInCache(self, appname, actorname, modelname, fields, fieldids, fieldnames):
        actor, model = self.getActorModel(appname, actorname, modelname)
        cacheinfo = {}
        cacheinfo["modelname"] = modelname
        cacheinfo["fields"] = fields
        cacheinfo["fieldids"] = fieldids
        cacheinfo["fieldnames"] = fieldnames

        key = j.base.idgenerator.generateGUID()
        actor.dbmem.cacheSet(key, cacheinfo)

        print "key:%s" % key

        return key

    def processLink(self, line):
        if line.find("[") != -1:
            r = "\[[-:@|_.?\w\s\\=/]*\]"
            if j.codetools.regex.match(r, line):  # find links
                for match in j.codetools.regex.yieldRegexMatches(r, line):
                    # print "link: %s" % match.founditem
                    match2 = match.founditem.replace("[", "").replace("]", "")
                    if match2.find("|") != -1:
                        descr, link = match2.split("|", 1)
                    elif match2.find(":") != -1:
                        descr, link = match2.split(":", 1)
                    else:
                        link = match2
                        descr = link
                    if link.find(";") != -1:
                        space, pagename = link.split(";", 1)
                        link = "/%s/%s" % (space.lower().strip("/"), pagename.strip("/"))
                    # print "match:%s"%match.founditem
                    # print "getlink:%s" %page.getLink(descr,link)
                    line = line.replace(match.founditem, "<a href='%s'>%s</a>" % (link, descr))
        return line

    def executeMacro(self, row, field):

        try:
            for match in j.codetools.regex.getRegexMatches("\$\d*", field).matches:
                nr = int(match.founditem.replace("$", ""))
                field = field.replace(match.founditem, row[nr])
        except:
            raise RuntimeError("Cannot process macro string for row, row was %s, field was %s" % (row, field))

        field = self.processLink(field)
        if field.find("{{") != -1:
            field = j.core.portal.active.macroexecutorPage.processMacrosInWikiContent(field)

        return field

    def getDataFromActorModel(self, appname, actorname, modelname, fields, fieldids, fieldnames):
        actor, model = self.getActorModel(appname, actorname, modelname)
        inn = model.list(True)
        l = len(inn)
        if l > 1000:
            raise RuntimeError("for now max length of editable grid=1000, h appname:%s, actorname:%s, model:%s" %
                              (appname, actorname, modelname))

        result = {}
        result["sEcho"] = 1
        result["iTotalRecords"] = l
        result["iTotalDisplayRecords"] = l
        result["aaData"] = []
        for row in inn:
            r = []
            for field in fields:
                if j.basetype.integer.check(field):
                    r.append(row[field])
                elif j.basetype.string.check(field):
                    r.append(self.executeMacro(row, field))
                else:
                    # is function
                    field = field(row, field)
                    field = self.processLink(field)
                    r.append(field)

            result["aaData"].append(r)

        return result

from JumpScale import j


class DataTables():

    def __init__(self):
        self.inited = False
        self.cache = {}
        self.cacheg = {}
        self._osiscl = j.core.osis.getClient(user='root')
        self._catclient = dict()

    def getClient(self, namespace, category):
        key = '%s_%s' % (namespace, category)
        if key in self._catclient:
            return self._catclient[key]
        client = j.core.osis.getClientForCategory(self._osiscl, namespace, category)
        self._catclient[key] = client
        return client

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

    def storInCache(self, fieldids, fieldnames, fieldvalues, filters=None):
        cache = j.db.keyvaluestore.getMemoryStore('datatables')
        cacheinfo = {}
        cacheinfo["fieldnames"] = fieldnames
        cacheinfo["fieldids"] = fieldids
        cacheinfo["fieldvalues"] = fieldvalues
        cacheinfo["filters"] = filters
        key = j.base.idgenerator.generateGUID()
        cache.cacheSet(key, cacheinfo)
        return key

    def getFromCache(self, key):
        cache = j.db.keyvaluestore.getMemoryStore('datatables')
        return cache.cacheGet(key)

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

        field = field % row
        field = self.processLink(field)
        if field.find("{{") != -1:
            field = j.core.portal.active.macroexecutorPage.processMacrosInWikiContent(field)

        return field

    def getData(self, namespace, category, key, **kwargs):
        datainfo = self.getFromCache(key)
        fieldids = datainfo['fieldids']
        fieldvalues = datainfo['fieldvalues'] or fieldids
        filters = datainfo["filters"] or dict()
        filters = filters.copy()

        client = self.getClient(namespace, category)

        #pagin
        start = kwargs['iDisplayStart']
        size = kwargs['iDisplayLength']


        #sort
        sort = dict()
        if kwargs['iSortCol_0']:
            for i in xrange(int(kwargs['iSortingCols'])):
                colidx = kwargs['iSortCol_%s' % i]
                key = 'bSortable_%s' % colidx
                if kwargs[key] == 'true':
                    colname = fieldids[int(colidx)]
                    sort[colname] = 'asc' if kwargs['sSortDir_%s' % i] == 'asc' else 'desc'

        #filters
        for x in xrange(len(fieldids)):
            svalue = kwargs.get('sSearch_%s' % x)
            if kwargs['bSearchable_%s' % x] == 'true' and svalue:
                filters[fieldids[x]] = svalue

        total, inn = client.simpleSearch(filters, size=size, start=start, withtotal=True, sort=sort)
        result = {}
        result["sEcho"] = int(kwargs.get('sEcho', 1))
        result["iTotalRecords"] = total
        result["iTotalDisplayRecords"] = total
        result["aaData"] = []
        for row in inn:
            r = []
            for field, fieldid in zip(fieldvalues, fieldids):
                if field in row:
                    r.append(row[field])
                elif j.basetype.integer.check(field):
                    r.append(row[field])
                elif j.basetype.string.check(field):
                    r.append(self.executeMacro(row, field))
                else:
                    # is function
                    field = field(row, fieldid)
                    field = self.processLink(field)
                    r.append(field)

            result["aaData"].append(r)

        return result

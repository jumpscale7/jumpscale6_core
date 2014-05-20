from JumpScale import j
import re
import os


class HeaderTools():

    @staticmethod
    def getHeadnr(line):
        if line.find(".") != -1:
            part1, part2 = line.strip().split(".", 1)
            part1 = part1.lower()
            headingnr = int(part1.replace("h", ""))
            return headingnr, part2
        else:
            return None, line

    @staticmethod
    def findLowestHeading(content):
        lowest = None
        for line in content.split("\n"):
            if re.match(r"\Ah\d+\. ", line, re.IGNORECASE):
                hnr, line = HeaderTools.getHeadnr(line)
                if hnr < lowest or lowest == None:
                    lowest = hnr
        return lowest


class Doc(object):

    def __init__(self, docpreprocessor):
        self.name = ""
        self.appliedparams = dict()
        self.alias = []
        self.pagename = ""
        self.source = ""
        self.author = []
        self.products = []
        self.visibility = ["public"]  # std PUBLIC,INTERNAL
        self.visible = True
        self.destructed = False
        self.docContentChanged = False
        self.content = ""
        self.path = ""
        self._mtime = 0
        self.shortpath = ""
        self.md5 = ""
        self.title = ""
        self.tags = ""  # jumpscale tags & labels
        self.type = ""  # def,concept,releasnote,...
        self.contenttype = "C"  # C or RST
        self.parent = ""
        self.generate = True
        self.order = 0
        self.children = []  # list of docs which are the children
        self.images = {}
        self.preprocessor = docpreprocessor
        self.dirty = True  # means document needs to be processed again e.g. macro's
        self.params = []
        self.docparams = {}
        self.defaultPath = ""
        self.usedefault = False
        self.hasMacros = False
        self.navigation = ""
        self.key = j.base.idgenerator.generateGUID()
        self.htmlHeadersCustom = []  # are extra html elements to be used which do not come from wiki
        self.htmlBodiesCustom = []
        self.processDefs = False
        self.space_path = None

    def copy(self):
        newdoc = Doc(self.preprocessor)
        newdoc.__dict__ = self.__dict__.copy()
        return newdoc

    def getSpaceName(self):
        return self.preprocessor.spacename

    def getPageKey(self):
        key = j.base.byteprocessor.hashMd5("%s_%s" % (self.pagename, self.getSpaceName()))
        j.core.portal.active.pageKey2doc[key] = self
        return key

    def checkVisible(self, visibility):
        if "*" in self.visibility:
            self.visible = True
            return
        if visibility == []:
            self.visible = True
            return
        for item in visibility:
            if item in self.visibility:
                self.visible = True
                return
        self.visible = False

    def loadFromDisk(self, preprocess=True):
        stat = os.stat(self.path)
        if stat.st_mtime > self._mtime:
            self._mtime = stat.st_mtime
            self.source = j.system.fs.fileGetTextContents(self.path)

        self.source = self.source.replace("\r\n", "\n")
        self.source = self.source.replace("\n\r", "\n")
        self.source = self.source.replace("\r", "\n")
        self.loadFromSource(preprocess)

    def loadFromSource(self, preprocess=True):
        self.content = self.source
        if "@usedefault" in self.content:
            self.usedefault = True
        elif "@nodefault" in self.content:
            self.usedefault = False
        templates_def = re.findall(r'^@template\s+(.*?)\n', self.content)
        if templates_def:
            template_name = templates_def[0]
        else:
            template_name = None

        if template_name:
            template_path = j.system.fs.joinPaths(self.preprocessor.space_path, ".space", template_name + '.wiki')
            template = j.system.fs.fileGetContents(template_path)
            self.content = template.replace('{content}', self.source)
        elif self.defaultPath and self.usedefault:
            default = j.system.fs.fileGetTextContents(self.defaultPath)
            self.content = default.replace("{content}", self.source)

        if preprocess and self.source.strip() != "":
            # print path3
            j.tools.docpreprocessorparser.parseDoc(self)
            self.preprocess()

    def fixMinHeadingLevel(self, minLevel):
        """
        make sure min heading level is followed
        """
        minLevel = int(minLevel)
        minLevelInDoc = 100
        for line in self.content.split("\n"):
            if line.lower().strip()[0:3] in ["h1.", "h2.", "h3.", "h4.", "h5.", "h6.", "h7."]:
                # found title
                level = int(line.split(".")[0].replace("h", ""))
                if level < minLevelInDoc:
                    minLevelInDoc = level
        content = ""
        if minLevelInDoc < minLevel:
            extra = minLevel - minLevelInDoc
            for line in self.content.split("\n"):
                if line.lower().strip()[0:3] in ["h1.", "h2.", "h3.", "h4.", "h5.", "h6.", "h7."]:
                    # found title
                    level = int(line.split(".")[0].replace("h", ""))
                    line = "h%s. %s" % (level + extra, ".".join(line.split(".")[1:]))
                content += "%s\n" % line
            self.content = content

    def _convertToInternalFormat(self):
        if self.contenttype == "RST":
            raise RuntimeError("Cannot convert from RST to Confluence, needs to be implemented")
            self.contenttype = "C"

    def preprocess(self):
        """
        make sure format is confluence
        execute macro's
        fix min heading level
        clean format in preprocessing
        """
        if self.source == "":
            self.loadFromDisk()
       
        # print "preprocess %s" % self.name
        self._convertToInternalFormat()
        self.findParams()
        self.executeMacrosPreprocess()
        self.clean()
        self.dirty = False

    def getHtmlBody(self, paramsExtra={}, ctx=None):
        if self.source == "":
            self.loadFromDisk()
            self.preprocess()
        if self.dirty or (ctx != None and "reload" in ctx.params):
            self.loadFromDisk()
            self.preprocess()
        content, doc = self.executeMacrosDynamicWiki(paramsExtra, ctx)
        ws = j.core.portal.active
        page = ws.confluence2htmlconvertor.convert(content, doc=self, page=ws.getpage())
        return page.body

    def findParams(self):
        if self.source == "":
            self.loadFromDisk()

        if self.content.strip() == "":
            return

        result = j.codetools.regex.findAll("\$\$\w*", self.content)  # finds $$...

        result3 = []
        for item in result:  # make unique
            item = item.replace("$$", "")
            if item not in result3:
                result3.append(item.strip().lower())

        result3.sort()
        result3.reverse()  # makes sure we will replace the longest statements first when we fill in the params
        self.params = result3

    def applyParams(self, params, findfresh=False, content=None):
        """
        @param params is dict with as key the name (lowercase)
        """
        isdoccontent = content == self.content
        if findfresh:
            self.findParams()
    
        if params:
            self.appliedparams.update(params)
        if len(self.params) > 0:
            for param in self.params:
                if param in params:
                    if content == None:
                        content = re.sub("\$\$%s(?!\w)" % param, str(params[param]), self.content)
                    else:
                        content = re.sub("\$\$%s(?!\w)" % param, str(params[param]), content)
        if isdoccontent:
            self.content = content
        return content

    def executeMacrosPreprocess(self):
        if self.source == "":
            self.loadFromDisk()
        
        self.preprocessor.macroexecutorPreprocessor.execMacrosOnDoc(self)

        self.hasMacros = self.preprocessor.macroexecutorWiki.existsMacros(self)  # find the macro tags on the doc

    def executeMacrosDynamicWiki(self, paramsExtra={}, ctx=None):
        # print "execute dynamic %s" % self.name
        if self.docparams != {}:
            for key in self.docparams.keys():
                paramsExtra[key] = self.docparams[key]

        if "page" not in paramsExtra:
            paramsExtra["page"] = self.original_name

        if "space" not in paramsExtra:
            paramsExtra["space"] = self.getSpaceName()

        return self.preprocessor.macroexecutorWiki.execMacrosOnContent(content=self.content, doc=self, paramsExtra=paramsExtra, ctx=ctx)

    def generate2disk(self, outpath):
        if self.generate and self.visible:
            dirpath = j.system.fs.joinPaths(outpath, self.pagename)
            filepath = j.system.fs.joinPaths(dirpath, "%s.txt" % self.pagename)
            j.system.fs.createDir(dirpath)
            for image in self.images:
                if image in self.preprocessor.images:
                    filename = "%s_%s" % (self.pagename, image)
                self.content = self.content.replace("!%s" % image, "!%s" % filename)
                j.system.fs.copyFile(self.preprocessor.images[image], j.system.fs.joinPaths(dirpath, filename))
            j.system.fs.writeFile(filepath, self.content)
            for doc in self.children:
                doc.generate(dirpath)

    def clean(self, startHeading=None):
        if self.pagename == "":
            self.pagename = self.name
        out = ""
        linenr = 1
        lastHeading = None
        lastLineWasEmpty = False
        lowestHeading = HeaderTools.findLowestHeading(self.content)
        lastLineWasHeading = False
        for line in self.content.split("\n"):
            if line.strip() == "" and linenr == 1:
                continue
            linenr += 1
            if line.strip() == "":
                # if lastLineWasEmpty:
                #     continue
                out += "\n"
                # lastLineWasEmpty = True
                continue
            if lastLineWasHeading and lastLineWasEmpty == False:
                out += "\n"
            lastLineWasHeading = False
            lastLineWasEmpty = False
            # if line.strip()[0]=="#":
            #    continue
            if re.match(r"\Ah\d+\. ", line, re.IGNORECASE):
                lastLineWasHeading = True
                hnr, line2 = HeaderTools.getHeadnr(line)

                if startHeading != None:
                    hnr = hnr - lowestHeading + startHeading
                line = "h%s.%s" % (hnr, line2)
            out += line + "\n"
        self.content = out

    def __str__(self):
        ss = ""
        ss += "%s\n" % self.name
        ss += "parent:%s\n" % self.parent
        ss += "%s\n" % self.type
        ss += "%s\n" % self.alias
        ss += "%s\n" % self.pagename
        ss += "%s\n" % self.author
        ss += "%s\n" % self.products
        ss += "%s\n" % self.visibility
        ss += "%s\n" % self.path
        ss += "%s\n" % self.shortpath
        ss += "%s\n" % self.md5
        ss += "%s\n" % self.tags
        return ss

    def __repr__(self):
        return self.__str__()


class DocPreprocessor():

    def __init__(self, contentDirs=[], varsPath="", spacename=""):
        """
        @param contentDirs are the dirs where we will load wiki files from & parse
        @param varsPath is the file with fars (just multiple lines with something like customer = ABC Data)
        @param macrosPath is dir where macro's are they are in form of tasklets
        @param cacheDir if non std caching dir override here

        """
        self.varsPath = varsPath

        self.macroexecutorPreprocessor = j.core.portal.active.macroexecutorPreprocessor
        self.macroexecutorPage = j.core.portal.active.macroexecutorPage
        self.macroexecutorWiki = j.core.portal.active.macroexecutorWiki

        if spacename == "":
            raise RuntimeError("spacename cannot be empty")
        self.spacename = spacename
        self.ignoreDirs = ["/.hg*"]
        self.docs = []
        self.name2doc = {}  # key= name or alias
        self.nametype2doc = {}  # key is name_type
        self.author2docs = {}  # key is authorname
        self._errors = []
        self.params = {}
        self._parsed = {}
        if self.varsPath != "" and j.system.fs.exists(self.varsPath):
            lines = j.system.fs.fileGetContents(self.varsPath).split("\n")
            for line in lines:
                if line.strip() != "":
                    if line.strip()[0] != "#":
                        if line.find("=") != -1:
                            paramname, value = line.split("=")
                            self.params[paramname.lower()] = value.strip()
        self.images = {}

        if contentDirs != []:
            for contentdir in contentDirs:
                self.scan(contentdir)

    def docNew(self):
        return Doc(self)

    def docAdd(self, doc):
        if doc.pagename == "":
            doc.pagename = doc.name
        self.docs.append(doc)
        self.name2doc[doc.name.lower()] = doc
        self.nametype2doc["%s_%s" % (doc.name, doc.type)] = doc
        for alias in doc.alias:
            if alias.lower().strip() != "":
                self.name2doc[alias] = doc
                self.nametype2doc["%s_%s" % (alias, doc.type)] = doc
        for author in doc.author:
            if author not in self.author2docs:
                self.author2docs[author] = []
            self.author2docs[author].append(doc)

    def docGet(self, docname):

        if docname.lower() in self.name2doc:
            doc = self.name2doc[docname.lower()]
            if doc.dirty:
                doc.loadFromDisk()
                doc.preprocess()
            return doc
        raise RuntimeError("Could not find doc with name %s" % docname)

    def docExists(self, docname):
        return docname.lower() in self.name2doc

    def _pathIgnoreCheck(self, path):
        base = j.system.fs.getBaseName(path)
        if base.strip() == "":
            return False
        dirname = j.system.fs.getDirName(path, True)
        if dirname.find(".") == 0:
            return True
        if base.find(".tmb") == 0:
            return True
        if base.find(".quarantine") == 0:
            return True
        if path[0] == "_":
            return False
        for item in self.ignoreDirs:
            item = item.replace(".", "\\.")
            item = item.replace("*", ".*")
            if j.codetools.regex.match(item, path):
                return True
        return False

    def findDocs(self, types=[], products=[], nameFilter=None, parent=None, filterTagsLabels=None):

        if filterTagsLabels != None:
            if filterTagsLabels.tagExists("name"):
                nameFilter = filterTagsLabels.tagGet("name").lower()
            else:
                nameFilter = None

            if filterTagsLabels.tagExists("parent"):
                parent = filterTagsLabels.tagGet("parent").lower()
            else:
                parent = None

            if filterTagsLabels.tagExists("product"):
                products = filterTagsLabels.tagGet("product")
                products = [item.strip().lower() for item in products.split(",")]
            else:
                products = []

            if filterTagsLabels.tagExists("type"):
                types = filterTagsLabels.tagGet("type")
                types = [item.strip().lower() for item in types.split(",")]
            else:
                types = []

        result = []
        for doc in self.docs:
            typefound = False
            productfound = False
            namefound = False
            parentfound = False

            if parent == None:
                parentfound = True
            else:
                parentfound = doc.parent.lower() == parent.lower()

            if types == []:
                typefound = True
            else:
                if doc.type in types:
                    typefound = True

            if products == []:
                productfound = True
            else:
                for product in products:
                    if product in doc.products:
                        productfound = True

            if nameFilter == None:
                namefound = True
            else:
                if j.codetools.regex.match(nameFilter.lower(), doc.name.lower()):
                    namefound = True
                for alias in doc.alias:
                    if alias != "":
                        if j.codetools.regex.match(nameFilter.lower(), alias.lower()):
                            namefound = True
            if typefound and productfound and namefound and parentfound:
                result.append(doc)
        return result

    def scan(self, path):
        print "DOCPREPROCESSOR SCAN space:%s" % path
        self.space_path = path

        spaceconfigdir = j.system.fs.getDirName(path + "/" + ".space" + "/")
        if j.system.fs.exists(spaceconfigdir):
            lastDefaultPath = spaceconfigdir + "/default.wiki"
            defaultdir = path
            lastparamsdir = ""
            lastparams = {}
            paramscfgfile = j.system.fs.joinPaths(spaceconfigdir, "params.cfg")
            if j.system.fs.exists(paramscfgfile):
                paramsfile = j.system.fs.fileGetContents(paramscfgfile)
                lastparamsdir = path
                for line in paramsfile.split("\n"):
                    if line.strip() != "" and line[0] != "#":
                        param1, val1 = line.split("=", 1)
                        lastparams[param1.strip().lower()] = val1.strip()
            lastnavdir = path
            lastnav = j.system.fs.fileGetTextContents(spaceconfigdir + "/nav.wiki")
        else:
            raise RuntimeError("space dir needs to have a dir .space for %s" % path)
        docs = self._scan(path, defaultdir, lastDefaultPath, lastparams, lastparamsdir, lastnav, lastnavdir)
        # print "SCANDONE"
        for doc in docs:
            doc.loadFromDisk()

        self.findChildren()
        self.spacename = j.system.fs.getDirName(path, True).lower()

    def parseHtmlDoc(self, path):
        subject = j.system.fs.fileGetTextContents(path)
        head = j.codetools.regex.findHtmlBlock(subject, "head", path, False)
        body = j.codetools.regex.findHtmlBlock(subject, "body", path, True)
        return head, body

    def _scan(self, path, defaultdir="", lastDefaultPath="", lastparams={}, lastparamsdir="",
              lastnav="", lastnavdir="", parent="", docs=[]):
        """
        directory to walk over and find story, task, ... statements
        """

        images = j.system.fs.listFilesInDir(path, True)
        for image in images:
            image2 = image.lower()
            if image2.find(".jpg") != -1 or image2.find(".jpeg") != -1 or image2.find(".png") != -1 or image2.find(".gif") != -1:
                image2 = image2.strip()
                image2 = j.system.fs.getBaseName(image2.replace("\\", "/"))
                self.images[image2] = image

        files = j.system.fs.listFilesInDir(path, False)
        parent2 = j.system.fs.getDirName(path + "/", True).lower()
        files.sort()

        def checkDefault(path, name):
            name2 = j.system.fs.getDirName(path, True).lower()
            if name == name2:
                return True
            dirpath = j.system.fs.getDirName(path)
            return j.system.fs.exists(j.system.fs.joinPaths(dirpath, ".usedefault"))

        def isRootDir(path):
            "check if dir is a bucket, actor or space dir, if yes should not descend"
            dirname = j.system.fs.getDirName(path + "/", True).lower()
            if dirname[0] == ".":
                return True
            # check if .space or .bucket or .actor in directory (subdir) if so return False
            for item in [".space", ".bucket", ".actor"]:
                if j.system.fs.exists(j.system.fs.joinPaths(path, item)):
                    return True
            return False
        lastBaseNameHtmlLower = ""
        for pathItem in files:
            if not self._pathIgnoreCheck(pathItem):
                basename = j.system.fs.getBaseName(pathItem).lower()
                # print "basename:%s" % basename

                # DEAL WITH DEFAULTS & NAVIGATIONS
                if pathItem.find(lastparamsdir) != 0:
                    # previous default does not count
                    lastparamsdir = ""
                    lastparams = {}
                if pathItem.find(defaultdir) != 0:
                    # previous default does not count
                    defaultdir = ""
                    lastDefaultPath = ""
                if pathItem.find(lastnavdir) != 0:
                    print "CANCEL lastnav %s cancel" % lastnavdir
                    lastnavdir = ""
                    lastnav = ""
                if basename == ".nav.wiki" or basename == "nav.wiki":
                    lastnav = j.system.fs.fileGetTextContents(pathItem)
                    lastnavdir = j.system.fs.getDirName(pathItem)
                    continue
                if basename == ".default.wiki" or basename == "default.wiki":
                    lastDefaultPath = pathItem
                    defaultdir = j.system.fs.getDirName(pathItem)
                    continue
                if basename == "params.cfg" or basename == ".params.cfg" or basename == "params" or basename == ".params":
                    paramsfile = j.system.fs.fileGetContents(pathItem)
                    lastparamsdir = j.system.fs.getDirName(pathItem)

                    for line in paramsfile.split("\n"):
                        if line.strip() != "" and line[0] != "#":
                            param1, val1 = line.split("=", 1)
                            paramskey = os.path.normpath(lastparamsdir)
                            if paramskey in lastparams:
                                newparams = lastparams[paramskey]
                                newparams[param1.strip().lower()] = val1.strip()
                            else:
                                newparams = {param1.strip().lower(): val1.strip()}
                            lastparams[paramskey] = newparams
                    continue

                # print pathItem
                # print "lastnav %s" % lastnavdir

                # path2 is relative part of path
                if pathItem.find(path) == 0:
                    path2 = pathItem[len(path):]
                else:
                    path2 = pathItem

                # print "parse %s" % path2
                # normalize relative path call path3
                if path2[0] == "/" or path2[0] == "\\":
                    path3 = path2[1:]
                else:
                    path3 = path2

                # process the html docs
                if j.system.fs.getFileExtension(pathItem) == "html":
                    # because of sorting html doc should always come first
                    lastBaseNameHtml = j.system.fs.getBaseName(pathItem).replace(".html", "")
                    if lastBaseNameHtml[0] not in ["_", "."]:
                        lastDirHtml = j.system.fs.getDirName(pathItem)
                        wikiCorrespondingPath = j.system.fs.joinPaths(lastDirHtml, lastBaseNameHtml + ".wiki")
                        if not j.system.fs.exists(wikiCorrespondingPath):
                            C = "@usedefault\n\n{{htmlloadheader}}\n\n{{htmlloadbody}}\n"
                            j.system.fs.writeFile(wikiCorrespondingPath, C)
                        lastHeaderHtml, lastBodyHtml = self.parseHtmlDoc(pathItem)
                        lastBaseNameHtmlLower = lastBaseNameHtml.lower()

                if j.system.fs.getFileExtension(pathItem) == "wiki":

                    # print "lastdefaultpath:%s" % lastDefaultPath
                    doc = self.docNew()
                    doc.original_name = j.system.fs.getBaseName(pathItem).replace(".wiki", "")
                    doc.name = doc.original_name.lower()
                    print "doc:%s path:%s" % (doc.name, pathItem)
                    if checkDefault(pathItem, doc.name):
                        # print "default %s" %lastDefaultPath
                        doc.parent = parent
                        doc.usedefault = True
                    else:
                        doc.parent = parent2

                    doc.defaultPath = lastDefaultPath

                    if doc.name == lastBaseNameHtmlLower:
                        # found corresponding wiki doc
                        doc.htmlHeadersCustom.append(lastHeaderHtml)
                        doc.htmlBodiesCustom.append(lastBodyHtml)

                    docdir = os.path.normpath(j.system.fs.getDirName(pathItem))
                    while(docdir != ''):
                        if docdir in lastparams:
                            newparams = lastparams[docdir]
                            if doc.docparams:
                                doc.docparams = newparams.update(doc.docparams)
                            else:
                                doc.docparams = newparams
                        docdir = j.system.fs.getParent(docdir)
                    # print "**********lastnav"
                    # print lastnav
                    # print "**********lastnavend"
                    doc.navigation = lastnav
                    doc.path = pathItem  # .replace("\\","/")
                    doc.shortpath = path3
                    self.docAdd(doc)
                    docs.append(doc)

        ddirs = j.system.fs.listDirsInDir(path, False)
        # print "dirs:%s" % ddirs
        for ddir in ddirs:
            if not isRootDir(ddir):
                self._scan(ddir, defaultdir, lastDefaultPath, lastparams, lastparamsdir,
                           lastnav, lastnavdir, parent=parent2)

        return docs

    def findChildren(self):
        for doc in self.docs:
            if doc.parent != "":
                if doc.parent in self.name2doc:
                    #from JumpScale.core.Shell import ipshellDebug,ipshell
                    # print "DEBUG NOW "
                    # ipshell()

                    #raise RuntimeError("Could not find parent %s for doc %s" % (doc.parent,doc.path))
                # else:
                    self.name2doc[doc.parent].children.append(doc)

    def __str__(self):
        ss = ""
        ss += "%s\n" % self.docs
        return ss

    def __repr__(self):
        return self.__str__()

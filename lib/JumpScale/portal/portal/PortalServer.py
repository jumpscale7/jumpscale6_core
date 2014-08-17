import re
import urlparse
import pprint
import os
import sys
import redis

from beaker.middleware import SessionMiddleware
from MacroExecutor import MacroExecutorPage, MacroExecutorWiki, MacroExecutorPreprocess
from PortalAuthenticatorOSIS import PortalAuthenticatorOSIS
from RequestContext import RequestContext
from PortalRest import PortalRest
from .OsisBeaker import OsisBeaker

from JumpScale import j
from gevent.pywsgi import WSGIServer
import gevent
import time

import mimeparse
import mimetypes
import JumpScale.grid.agentcontroller

BLOCK_SIZE = 4096

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_JS = 'application/javascript'
CONTENT_TYPE_YAML = 'application/yaml'
CONTENT_TYPE_PLAIN = 'text/plain'
CONTENT_TYPE_HTML = 'text/html'
CONTENT_TYPE_PNG = 'image/png'


class PortalServer:

##################### INIT
    def __init__(self):

        self.hrd=j.application.instanceconfig

        self.contentdirs = list()
        self.libpath = j.html.getHtmllibDir()
        self.started = False
        self.epoch = time.time()

        self.cfgdir="cfg"

        j.core.portal.active=self

        osisinstance=self.hrd.get("portal.osis.connection")

        self.osis =j.core.osis.getClientByInstance(osisinstance)

        self.pageKey2doc = {}
        self.routes = {}

        self.loadConfig()        

        macroPathsPreprocessor = ["macros/preprocess"]
        macroPathsWiki = ["macros/wiki"]
        macroPathsPage = ["macros/page"]

        self.macroexecutorPreprocessor = MacroExecutorPreprocess(macroPathsPreprocessor)
        self.macroexecutorPage = MacroExecutorPage(macroPathsPage)
        self.macroexecutorWiki = MacroExecutorWiki(macroPathsWiki)

        self.bootstrap()

        session_opts = {
            'session.cookie_expires': False,
            'session.type': 'OsisBeaker',
            'session.namespace_class': OsisBeaker,
            'session.namespace_args': {'client': self.osis},
            'session.data_dir': '%s' % j.system.fs.joinPaths(j.dirs.varDir, "beakercache")
        }
        self._router = SessionMiddleware(self.router, session_opts)
        self._webserver = WSGIServer((self.listenip, self.port), self._router)

        # wwwroot = wwwroot.replace("\\", "/")
        # while len(wwwroot) > 0 and wwwroot[-1] == "/":
        #     wwwroot = wwwroot[:-1]
        # self.wwwroot = wwwroot

        self.confluence2htmlconvertor = j.tools.docgenerator.getConfluence2htmlConvertor()
        self.activejobs = list()
        self.jobids2greenlets = dict()

        self.schedule1min = {}
        self.schedule15min = {}
        self.schedule60min = {}

        self.rediscache=redis.StrictRedis(host='localhost', port=7767, db=0)
        self.redisprod=redis.StrictRedis(host='localhost', port=7768, db=0)

        self.jslibroot=j.system.fs.joinPaths(j.dirs.baseDir,"apps","portals","jslib")

        self.auth=PortalAuthenticatorOSIS()

        self.loadSpaces()

        self.rest=PortalRest(self)        

    def loadConfig(self):

        def replaceVar(txt):
            # txt = txt.replace("$base", j.dirs.baseDir).replace("\\", "/")
            txt = txt.replace("$appdir", j.system.fs.getcwd()).replace("\\", "/")
            txt = txt.replace("$vardir", j.dirs.varDir).replace("\\", "/")
            txt = txt.replace("$htmllibdir", j.html.getHtmllibDir()).replace("\\", "/")
            txt = txt.replace("\\", "/")
            return txt


        ######INIT FILE

        ini = j.tools.inifile.open(self.cfgdir + "/portal.cfg")

        if ini.checkParam("main", "appdir"):
            self.appdir = replaceVar(ini.getValue("main", "appdir"))
            self.appdir=self.appdir.replace("$base",j.dirs.baseDir)
        else:
            self.appdir = j.system.fs.getcwd()

        self.getContentDirs() #contentdirs need to be loaded before we go to other dir of base server
        j.system.fs.changeDir(self.appdir)            

        # dbtype = ini.getValue("main", "dbtype").lower().strip()
        # if dbtype == "fs":
        #     self.dbtype = j.enumerators.KeyValueStoreType.FILE_SYSTEM
        # elif dbtype == "mem":
        #     self.dbtype = j.enumerators.KeyValueStoreType.MEMORY
        # elif dbtype == "redis":
        #     self.dbtype = j.enumerators.KeyValueStoreType.REDIS
        # elif dbtype == "arakoon":
        #     self.dbtype = j.enumerators.KeyValueStoreType.ARAKOON
        # else:
        #     raise RuntimeError("could not find appropriate core db, supported are: fs,mem,redis,arakoon, used here'%s'"%dbtype)

        # self.systemdb=j.db.keyvaluestore.getFileSystemStore("appserversystem",baseDir=replaceVar(ini.getValue("systemdb","dbdpath")))

        self.listenip = '0.0.0.0'
        if ini.checkSection('main') and ini.checkParam('main', 'listenip'):
            self.listenip = ini.getValue('main', 'listenip')

        self.port = int(ini.getValue("main", "webserverport"))
        self.addr = ini.getValue("main", "pubipaddr")

        self.logdir= j.system.fs.joinPaths(j.dirs.logDir,"portal",str(self.port))
        j.system.fs.createDir(self.logdir)



        # self.secret = ini.getValue("main", "secret")
        self.admingroups = ini.getValue("main", "admingroups").split(",")

        self.filesroot = replaceVar(ini.getValue("main", "filesroot"))

        j.system.fs.createDir(self.filesroot)

        self.getContentDirs()

    def reset(self):
        self.routes={}
        self.loadConfig()
        self.bootstrap()        
        j.core.codegenerator.resetMemNonSystem()
        j.core.specparser.resetMemNonSystem()
        # self.actorsloader.scan(path=self.contentdirs,reset=True) #do we need to load them all
        self.bucketsloader = j.core.portalloader.getBucketsLoader()
        self.spacesloader = j.core.portalloader.getSpacesLoader()
        self.loadSpaces()
        
    def bootstrap(self):
        self.actors = {}  # key is the applicationName_actorname (lowercase)
        self.actorsloader = j.core.portalloader.getActorsLoader()
        self.app_actor_dict = {}
        self.taskletengines = {}        
        self.actorsloader.reset()
        # self.actorsloader._generateLoadActor("system", "contentmanager", actorpath="%s/apps/portalbase/system/system__contentmanager/"%j.dirs.baseDir)
        # self.actorsloader._generateLoadActor("system", "master", actorpath="system/system__master/")
        # self.actorsloader._generateLoadActor("system", "usermanager", actorpath="system/system__usermanager/")
        self.actorsloader.scan(self.contentdirs)
        self.actorsloader.getActor("system", "contentmanager")
        self.actorsloader.getActor("system", "usermanager")

    def loadSpaces(self):

        self.bucketsloader = j.core.portalloader.getBucketsLoader()
        self.spacesloader = j.core.portalloader.getSpacesLoader()
        self.bucketsloader.scan(self.contentdirs)

        self.spacesloader.scan(self.contentdirs)

        if "system" not in self.spacesloader.spaces:
            raise RuntimeError("could not find system space")

        self.spacesloader.spaces["system"].loadDocProcessor() #need to make sure we have content for the systemspace

    def getContentDirs(self):
        """
        walk over known content dirs & execute loader on it
        """
        cfgpath = j.system.fs.joinPaths(self.cfgdir, "contentdirs.cfg")

        def append(path):
            path=j.system.fs.pathNormalize(path)
            if path not in self.contentdirs:
                self.contentdirs.append(path)

        if j.system.fs.exists(cfgpath):
            wikicfg = j.system.fs.fileGetContents(cfgpath)

            paths = wikicfg.split("\n")

            for path in paths:
                path = path.strip()
                if path=="" or path[0]=="#":
                    continue
                path=path.replace("\\","/")
                if path[0] != "/" and path.find(":") == -1:
                    path = j.system.fs.joinPaths(j.system.fs.getParent(self.cfgdir), path)
                append(path)

        #add own base path
        self.basepath = j.system.fs.joinPaths(j.system.fs.getParent(self.cfgdir), "base")
        j.system.fs.createDir(self.basepath)
        append(self.basepath)

        #add base path of parent portal
        appdir = self.appdir
        append(j.system.fs.joinPaths(appdir, "wiki"))
        append(j.system.fs.joinPaths(appdir, "system"))

    def unloadActorFromRoutes(self, appname, actorname):
        for key in self.routes.keys():
            appn, actorn, remaining = key.split("_", 2)
            # print appn+" "+appname+" "+actorn+" "+actorname
            if appn == appname and actorn == actorname:
                self.routes.pop(key)
 
##################### USER RIGHTS

    def getUserRight(self, ctx, space):
        if space == "" or space not in self.spacesloader.spaces:
            space = "system"
        spaceobject = self.spacesloader.spaces[space]
        # print "spaceobject"
        # print spaceobject.model
        if "user" in ctx.env['beaker.session']:
            username = ctx.env['beaker.session']["user"]
        else:
            username = ""
        if username == "":
            right = ""
        else:
            
            if username=="guest":
                groupsusers=["guest","guests"]
            else:
                groupsusers=self.auth.getGroups(username)

            right = ""
            if "admin" in groupsusers:
                right = "*"
            # print "groupsusers:%s"%groupsusers
            if right == "":
                for groupuser in groupsusers:
                    if groupuser in spaceobject.model.acl:
                        # found match
                        right = spaceobject.model.acl[groupuser]
                        break

            # if right == "":
            #     #check bitbucket
            #     for key,acl in spaceobject.model.acl.iteritems():
            #         if key.find("bitbucket")==0:
            #             from IPython import embed
            #             print "DEBUG NOW ooooooo"
            #             embed()
                        
        if right == "*":
            right = "rwa"
        # print "right:%s" % right
        return username, right

    def getUserFromCTX(self,ctx):
        return str(ctx.env["beaker.session"]["user"])

    def getGroupsFromCTX(self,ctx):
        groups=self.auth.getGroups(ctx.env["beaker.session"]["user"])
        return [str(item.lower()) for item in groups]

    def isAdminFromCTX(self,ctx):
        groups=self.getGroupsFromCTX(ctx)
        for gr in groups:
            if gr in self.admingroups:
                return True
        return False     

    def isLoggedInFromCTX(self,ctx):
        user=self.getUserFromCTX(ctx)
        if user<>"" and user<>"guest":
            return True
        return False

##################### process pages, get docs
    def getpage(self):
        page = j.tools.docgenerator.pageNewHTML("index.html", htmllibPath="/jslib")
        return page

    def sendpage(self, page, start_response):
        contenttype = "text/html"
        start_response('200 OK', [('Content-Type', contenttype), ])
        return [page.getContent()]

    def getDoc(self, space, name, ctx, params={}):
        print "GETDOC:%s" % space
        space = space.lower()
        name = name.lower()

        username, right = self.getUserRight(ctx, space)

        if name in ["login", "error", "accessdenied", "pagenotfound"]:
            right = "r"

        print "# space:%s name:%s user:%s right:%s" % (space, name, username, right)

        if space == "" and name == "":
            space = "system"
            if not "r" in right:
                name = "accessdenied"
            else:
                name = "spaces"

        if name != "accessdenied" and name != "pagenotfound":
            # check security
            if right == "":
                params["space"] = space
                params["page"] = name
                doc, params = self.getDoc(space, "accessdenied", ctx, params=params)
                return doc, params
        else:
            right = "r"

        # print "find space:%s page:%s" % (space,name)
        if space == "":
            doc, params = self.getDoc("system", "spaces", ctx, params)
            # ctx.params["error"]="Could not find space, space was empty, please specify space.\n"
        elif space not in self.spacesloader.spaces:
            if space == "system":
                raise RuntimeError("wiki has not loaded system space, cannot continue")
            print "could not find space %s" % space
            doc, params = self.getDoc("system", "pagenotfound", ctx, params)
            if "space" not in params:
                params["space"] = space
            if "page" not in params:
                params["page"] = name
            print "could not find space %s" % space
            ctx.params["error"] = "Could not find space %s\n" % space
        else:
            spaceObject = self.spacesloader.getLoaderFromId(space)

            if spaceObject.docprocessor == None:
                spaceObject.loadDocProcessor(force=True)  # dynamic load of space

            spacedocgen = spaceObject.docprocessor

            if name != "" and name in spacedocgen.name2doc:
                doc = spacedocgen.name2doc[name]
            else:
                if name == "accessdenied":
                    # means the accessdenied page does not exist
                    doc, params = self.getDoc("system", "accessdenied", ctx, params)
                    return doc, params
                if name == "pagenotfound":
                    # means the nofound page does not exist
                    doc, params = self.getDoc("system", "pagenotfound", ctx, params)
                    ctx.start_response("404 Not found", [])
                    return doc, params
                if name == "":
                    if space in spacedocgen.name2doc:
                        doc = spacedocgen.name2doc[space]
                    elif "home" in spacedocgen.name2doc:
                        doc = spacedocgen.name2doc["home"]
                    else:
                        ctx.params["path"] = "space:%s pagename:%s" % (space, name)
                        # print ctx.params["path"]
                        if "space" not in params:
                            params["space"] = space
                        if "page" not in params:
                            params["page"] = name
                        doc, params = self.getDoc(space, "pagenotfound", ctx, params)
                else:
                    ctx.params["path"] = "space:%s pagename:%s" % (space, name)
                    doc, params = self.getDoc(space, "pagenotfound", ctx, params)

        ctx.params["rights"] = right
        doc.loadFromDisk()

        if name == "pagenotfound":
            ctx.start_response("404 Not found", [])

        return doc, params

    def returnDoc(self, ctx, start_response, space, docname, extraParams={}):
        doc, params = self.getDoc(space, docname, ctx, params=ctx.params)

        if doc.dirty or "reload" in ctx.params:
            doc.loadFromDisk()
            doc.preprocess()

        ctx.params.update(extraParams)

        # doc.applyParams(ctx.params)
        content,doc = doc.executeMacrosDynamicWiki(paramsExtra=extraParams, ctx=ctx)

        page = self.confluence2htmlconvertor.convert(content, doc=doc, requestContext=ctx, page=self.getpage(), paramsExtra=ctx.params)

        if not 'postprocess' in page.processparameters or page.processparameters['postprocess']:
            page.body = page.body.replace("$$space", space)
            page.body = page.body.replace("$$page", doc.original_name)
            page.body = page.body.replace("$$path", doc.path)
            page.body = page.body.replace("$$querystr", ctx.env['QUERY_STRING'])

        page.body = page.body.replace("$$$menuright", "")

        if "todestruct" in doc.__dict__:
            doc.destructed = True

        ctx.start_response('200 OK', [('Content-Type', "text/html"), ])
        return page

    def processor_page(self, environ, start_response, wwwroot, path, prefix="", webprefix="", index=False):
        def indexignore(item):
            ext = item.split(".")[-1].lower()
            if ext in ["pyc", "pyo", "bak"]:
                return True
            if item[0] == "_":
                return True
            if item[0] == ".":
                return True
            return False

        def formatContent(contenttype, path, template, start_response):
            content = j.system.fs.fileGetContents(path)
            page = self.getpage()
            page.addCodeBlock(content, template, edit=True)
            start_response('200 OK', [('Content-Type', contenttype), ])
            return [str(page)]

        def removePrefixes(path):
            path = path.replace("\\", "/")
            path = path.replace("//", "/")
            path = path.replace("//", "/")
            while len(path) > 0 and path[0] == "/":
                path = path[1:]
            while path.find(webprefix + "/") == 0:
                path = path[len(webprefix) + 1:]
            while path.find(prefix + "/") == 0:
                path = path[len(prefix) + 1:]
            return path

        def send_file(file_path, size):
            # print "sendfile:%s" % path
            f = open(file_path, "rb")
            block = f.read(BLOCK_SIZE * 10)
            BLOCK_SIZE2 = 0
            # print "%s %s" % (file_path,size)
            while BLOCK_SIZE2 < size:
                BLOCK_SIZE2 += len(block)
                # print BLOCK_SIZE2
                # print len(block)
                yield block
                block = f.read(BLOCK_SIZE)
            # print "endfile"

        wwwroot = wwwroot.replace("\\", "/").strip()

        path = removePrefixes(path)

        # print "wwwroot:%s" % wwwroot
        if not wwwroot.replace("/", "") == "":
            pathfull = wwwroot + "/" + path

        else:
            pathfull = path

        contenttype = "text/html"
        content = ""
        headers = list()
        ext = path.split(".")[-1].lower()
        contenttype = mimetypes.guess_type(pathfull)[0]

        if path == "favicon.ico":
            pathfull = "wiki/System/favicon.ico"

        if not j.system.fs.exists(pathfull) and j.system.fs.exists(pathfull + '.gz') and 'gzip' in environ.get('HTTP_ACCEPT_ENCODING'):
            pathfull += ".gz"
            headers.append(('Vary', 'Accept-Encoding'))
            headers.append(('Content-Encoding', 'gzip'))

        if not j.system.fs.exists(pathfull):
            print "error"
            headers = [('Content-Type', contenttype), ]
            start_response("404 Not found", headers)
            return ["path %s not found" % path]

        size = os.path.getsize(pathfull)

        if ext == "wiki":
            contenttype = "text/html"
            # return formatWikiContent(pathfull,start_response)
            return formatContent(contenttype, pathfull, "python", start_response)
        elif ext == "py":
            contenttype = "text/html"
            return formatContent(contenttype, pathfull, "python", start_response)
        elif ext == "spec":
            contenttype = "text/html"
            return formatContent(contenttype, pathfull, "python", start_response)

        # print contenttype

        status = '200 OK'

        headers.append(('Content-Type', contenttype))
        headers.append(("Content-length", str(size)))
        headers.append(("Cache-Control", 'public,max-age=3600'))

        start_response(status, headers)

        if content != "":
            return [content]
        else:
            return send_file(pathfull, size)

    def process_elfinder(self, path, ctx):
        from JumpScale.portal.html import elFinder
        db = j.db.keyvaluestore.getMemoryStore('elfinder')
        rootpath = db.cacheGet(path)
        options = {'root': rootpath, 'dotFiles': True}
        con = elFinder.connector(options)
        params = ctx.params.copy()

        if 'rawdata' in params:
            from JumpScale.portal.html import multipart
            from cStringIO import StringIO
            ctx.env.pop('wsgi.input', None)
            stream = StringIO(ctx.params.pop('rawdata'))
            forms, files = multipart.parse_form_data(ctx.env, stream=stream)
            params.update(forms)
            for key, value in files.iteritems():
                if key == 'upload[]':
                    params['upload[]'] = dict()
                    params['upload[]'][value.filename] = value.file
        if params.get('init') == '1':
            params.pop('target', None)
        status, header, response = con.run(params)
        status = '%s' % status
        headers = [ (k, v) for k,v in header.iteritems() ]
        ctx.start_response(status, headers)
        if 'download' not in params:
            response = j.db.serializers.getSerializerType('j').dumps(response)
        else:
            response = response['content']
        return [response]

    def path2spacePagename(self, path):

        pagename = ""
        if path.find("?") != -1:
            path = path.split("?")[0]
        while len(path) > 0 and path[-1] == "/":
            path = path[:-1]
        if path.find("/") == -1:
            space = path.strip()
        else:
            splitted = path.split("/")
            space = splitted[0].lower()
            pagename = splitted[-1].lower()

        return space, pagename

##################### FORMATTING + logs/raiseerror
    def log(self, ctx, user, path, space="", pagename=""):
        path2 = j.system.fs.joinPaths(self.logdir, "user_%s.log" % user)

        epoch = j.base.time.getTimeEpoch() + 3600 * 6
        hrtime = j.base.time.epoch2HRDateTime(epoch)

        if False and self.geoIP != None:  # @todo fix geoip, also make sure nginx forwards the right info
            ee = self.geoIP.record_by_addr(ctx.env["REMOTE_ADDR"])
            loc = "%s_%s_%s" % (ee["area_code"], ee["city"], ee["region_name"])
        else:
            loc = ""

        msg = "%s|%s|%s|%s|%s|%s|%s\n" % (hrtime, ctx.env["REMOTE_ADDR"], epoch, space, pagename, path, loc)
        j.system.fs.writeFile(path2, msg, True)

        if space != "":
            msg = "%s|%s|%s|%s|%s|%s|%s\n" % (hrtime, ctx.env["REMOTE_ADDR"], epoch, user, pagename, path, loc)
            pathSpace = j.system.fs.joinPaths(self.logdir, "space_%s.log" % space)
            j.system.fs.writeFile(pathSpace, msg, True)

    def raiseError(self, ctx, msg="", msginfo="", errorObject=None, httpcode="500 Internal Server Error"):
        """
        """
        if not ctx.checkFormat():
            # error in format
            eco = j.errorconditionhandler.getErrorConditionObject()
            eco.errormessage = "only format supported = human or json, format is put with param &format=..."
            eco.type = j.enumerators.ErrorConditionType.INPUT
            print "WRONG FORMAT"
        else:
            if errorObject != None:
                eco = errorObject
            else:
                eco = j.errorconditionhandler.getErrorConditionObject()

        scriptName = ctx.env["SCRIPT_NAME"]
        remoteAddress = ctx.env["REMOTE_ADDR"]
        queryString = ctx.env["QUERY_STRING"]

        eco.caller = remoteAddress
        if msg != "":
            eco.errormessage = msg
        else:
            eco.errormessage = ""
        if msginfo != "":
            eco.errormessage += "\msginfo was:\n%s" % msginfo
        if queryString != "":
            eco.errormessage += "\nquerystr was:%s" % queryString
        if scriptName != "":
            eco.errormessage += "\nscriptname was:%s" % scriptName

        j.errorconditionhandler.processErrorConditionObject(eco)

        if ctx.fformat == "human" or ctx.fformat == "text":
            if msginfo != None and msginfo != "":
                msg += "\n<br>%s" % msginfo
            else:
                msg += "\n%s" % eco
                msg = self._text2html(msg)

        else:
            # is json
            # result=[]
            # result["error"]=eco.obj2dict()
            def todict(obj):
                data = {}
                for key, value in obj.__dict__.iteritems():
                    try:
                        data[key] = todict(value)
                    except AttributeError:
                        data[key] = value
                return data
            eco.tb=""
            eco.frames=[]
            msg = j.db.serializers.getSerializerType('j').dumps(todict(eco))

        ctx.start_response(httpcode, [('Content-Type', 'text/html')])

        j.console.echo("***ERROR***:%s : method %s from ip %s with params %s" % (
            msg, scriptName, remoteAddress, queryString), 2)
        if j.application.debug:
            return msg
        else:
            return "An unexpected error has occurred, please try again later."

    def _text2html(self, text):
        text = text.replace("\n", "<br>")
        # text=text.replace(" ","&nbsp; ")
        return text

    def _text2htmlSerializer(self, content):
        return self._text2html(pprint.pformat(content))

    def _resultjsonSerializer(self, content):
        return j.db.serializers.getSerializerType('j').dumps({"result": content})

    def _resultyamlSerializer(self, content):
        return j.code.object2yaml({"result": content})

    def getMimeType(self, contenttype, format_types):
        supported_types = ["text/plain", "text/html", "application/yaml", "application/json"]
        CONTENT_TYPES = {
            "text/plain": str,
            "text/html": self._text2htmlSerializer,
            "application/yaml": self._resultyamlSerializer,
            "application/json": j.db.serializers.getSerializerType('j').dumps
        }

        if not contenttype:
            serializer = format_types["text"]["serializer"]
            return CONTENT_TYPE_HTML, serializer
        else:
            mimeType = mimeparse.best_match(supported_types, contenttype)
            serializer = CONTENT_TYPES[mimeType]
            return mimeType, serializer

    def reformatOutput(self, ctx, result, restreturn=False):
        FFORMAT_TYPES = {
            "text": {"content_type": CONTENT_TYPE_HTML, "serializer": self._text2htmlSerializer},
            "html": {"content_type": CONTENT_TYPE_HTML, "serializer": self._text2htmlSerializer},
            "raw": {"content_type": CONTENT_TYPE_PLAIN, "serializer": str},
            "jsonraw": {"content_type": CONTENT_TYPE_JSON, "serializer": j.db.serializers.getSerializerType('j').dumps},
            "json": {"content_type": CONTENT_TYPE_JSON, "serializer": self._resultjsonSerializer},
            "yaml": {"content_type": CONTENT_TYPE_YAML, "serializer": self._resultyamlSerializer}
        }

        if ctx._response_started:
            return None, result

        fformat = ctx.fformat
        if '_jsonp' in ctx.params:
            result = {'httpStatus': ctx.httpStatus, 'httpMessage': ctx.httpMessage, 'body': result}
            return CONTENT_TYPE_JS, "%s(%s);" % (ctx.params['_jsonp'], j.db.serializers.getSerializerType('j').dumps(result))


        if '_png' in ctx.params:
            return CONTENT_TYPE_PNG, result


        if "CONTENT_TYPE" not in ctx.env:
            ctx.env['CONTENT_TYPE'] = CONTENT_TYPE_PLAIN

        if ctx.env['CONTENT_TYPE'].find("form-") != -1:
            ctx.env['CONTENT_TYPE'] = CONTENT_TYPE_PLAIN
        # normally HTTP_ACCEPT defines the return type we should rewrite this
        if fformat:
            # extra format paramter overrides http_accept header
            return FFORMAT_TYPES[fformat]['content_type'], FFORMAT_TYPES[fformat]['serializer'](result)
        else:
            if 'HTTP_ACCEPT' in ctx.env:
                returntype = ctx.env['HTTP_ACCEPT']
            else:
                returntype = ctx.env['CONTENT_TYPE']
            content_type, serializer = self.getMimeType(returntype, FFORMAT_TYPES)
            return content_type, serializer(result)

##################### router

    def startSession(self, ctx, path):
        session = ctx.env['beaker.session']
        if "authkey" in ctx.params:
            # user is authenticated by a special key
            key = ctx.params["authkey"]

            if self.auth.existsKey(key):
                username = self.auth.getUserFromKey(key)
                session['user'] = username
                session.save()
            elif key == self.secret:
                session['user'] = 'admin'
                session.save()
            else:
                # check if authkey is a session
                newsession = session.get_by_id(key)
                if newsession:
                    session = newsession
                    ctx.env['beaker.session'] = session
                else:
                    ctx.start_response('419 Authentication Timeout', [])
                    return False, [str(self.returnDoc(ctx, ctx.start_response, "system", "accessdenied", extraParams={"path": path}))]

        if "user_logoff_" in ctx.params:
            session.delete()
            return False, [str(self.returnDoc(ctx, ctx.start_response, "system", "login", extraParams={"path": path}))]

        if "user_login_" in ctx.params:
            # user has filled in his login details, this is response on posted info
            name = ctx.params['user_login_']
            if not ctx.params.has_key('passwd'):
                secret=""
            else:
                secret = ctx.params['passwd']
            if self.auth.authenticate(name, secret):
                session['user'] = name
                if "querystr" in session:
                    ctx.env['QUERY_STRING'] = session['querystr']
                else:
                    ctx.env['QUERY_STRING'] = ""
                session.save()
                # user is loging in from login page redirect him to home
                if path.endswith('system/login'):
                    status = '302'
                    headers = [
                        ('Location', "/"),
                    ]
                    ctx.start_response(status, headers)
                    return False, [""]
            else:
                session['user'] = ""
                session["querystr"] = ""
                session.save()
                return False, [str(self.returnDoc(ctx, ctx.start_response, "system", "accessdenied", extraParams={"path": path}))]

        if "user" not in session or session["user"] == "":
            session['user'] = "guest"
            session.save()

        if "querystr" in session:
            session["querystr"] = ""
            session.save()

        return True, session

    def _getParamsFromEnv(self, env, ctx):
        params = urlparse.parse_qs(env["QUERY_STRING"])

        # HTTP parameters can be repeated multiple times, i.e. in case of using <select multiple>
        # Example: a=1&b=2&a=3
        #
        # urlparse.parse_qs returns a dictionary of names & list of values. Then it's simplified
        # for lists with only a single element, e.g.
        #
        #   {'a': ['1', '3'], 'b': ['2']}
        #
        # simplified to be
        #
        #   {'a': ['1', '3'], 'b': '2'}
        params = dict(((k, v) if len(v) > 1 else (k, v[0])) for k, v in params.items())

        if env["REQUEST_METHOD"] in ("POST", "PUT"):
            postData = env["wsgi.input"].read()
            if postData.strip() == "":
                return params
                msg = "postdata cannot be empty"
                self.raiseError(ctx, msg)
            if env['CONTENT_TYPE'].find("application/json") != -1:
                postParams = j.db.serializers.getSerializerType('j').loads(postData)
                if postParams:
                    params.update(postParams)
                return params
            elif env['CONTENT_TYPE'].find("www-form-urlencoded") != -1:
                params.update(dict(urlparse.parse_qsl(postData)))
                return params
            else:
                params['rawdata'] = postData
        return params

    def router(self, environ, start_response):
        path = environ["PATH_INFO"].lstrip("/")
        print "path:%s" % path
        pathparts = path.split('/')
        if pathparts[0] == 'wiki':
            pathparts = pathparts[1:]

        if path.find("favicon.ico") != -1:
            return self.processor_page(environ, start_response, self.filesroot, "favicon.ico", prefix="")

        ctx = RequestContext(application="", actor="", method="", env=environ,
                             start_response=start_response, path=path, params=None)
        ctx.params = self._getParamsFromEnv(environ, ctx)

        if path.find("jslib/") == 0:
            path = path[6:]
            user = "None"
            # self.log(ctx, user, path)
            return self.processor_page(environ, start_response, self.jslibroot, path, prefix="jslib/")

        if path.find("images/") == 0:
            space, image = pathparts[1:3]
            spaceObject = self.getSpace(space)
            image = image.lower()
            if image in spaceObject.docprocessor.images:
                path = spaceObject.docprocessor.images[image]
                return self.processor_page(environ, start_response, j.system.fs.getDirName(path), j.system.fs.getBaseName(path), prefix="images")
            ctx.start_response('404', [])

        if path.find("files/specs/") == 0:
            path = path[6:]
            user = "None"
            self.log(ctx, user, path)
            return self.processor_page(environ, start_response, self.filesroot, path, prefix="files/")

        if path.find(".files") != -1:
            user = "None"
            self.log(ctx, user, path)
            space = pathparts[0].lower()
            path = "/".join(pathparts[2:])
            sploader = self.spacesloader.getSpaceFromId(space)
            filesroot = j.system.fs.joinPaths(sploader.model.path, ".files")
            return self.processor_page(environ, start_response, filesroot, path, prefix="")

        # user is logged in now
        is_session, session = self.startSession(ctx, path)
        if not is_session:
            return session
        user = session['user']
        match = pathparts[0]
        path = ""
        if len(pathparts) > 1:
            path = "/".join(pathparts[1:])

        if match == "restmachine":
            return self.rest.processor_rest(environ, start_response, path, human=False, ctx=ctx)

        elif match == "elfinder":
            return self.process_elfinder(path, ctx)

        elif match == "restextmachine":
            return self.rest.processor_restext(environ, start_response, path, human=False, ctx=ctx)

        elif match == "rest":
            space, pagename = self.path2spacePagename(path.strip("/"))
            self.log(ctx, user, path, space, pagename)
            return self.rest.processor_rest(environ, start_response, path, ctx=ctx)

        elif match == "restext":
            space, pagename = self.path2spacePagename(path.strip("/"))
            self.log(ctx, user, path, space, pagename)
            return self.rest.processor_restext(environ, start_response, path,
                                          ctx=ctx)
        elif match == "ping":
            status = '200 OK'
            headers = [
                ('Content-Type', "text/html"),
            ]
            start_response(status, headers)
            return ["pong"]

        elif match == "files":
            self.log(ctx, user, path)
            return self.processor_page(environ, start_response, self.filesroot, path, prefix="files")

        elif match == "specs":
            return self.processor_page(environ, start_response, "specs", path, prefix="specs")

        elif match == "appservercode":
            return self.processor_page(environ, start_response, "code", path, prefix="code", webprefix="appservercode")

        elif match == "lib":
            # print self.libpath
            return self.processor_page(environ, start_response, self.libpath, path, prefix="lib")

        else:
            path = '/'.join(pathparts)
            ctx.params["path"] = '/'.join(pathparts)
            space, pagename = self.path2spacePagename(path)
            self.log(ctx, user, path, space, pagename)
            return [str(self.returnDoc(ctx, start_response, space, pagename, {}))]
    
    def addRoute(self, function, appname, actor, method, paramvalidation={}, paramdescription={}, \
        paramoptional={}, description="", auth=True, returnformat=None):
        """
        @param function is the function which will be called as follows: function(webserver,path,params):
            function can also be a string, then only the string will be returned
            if str=='taskletengine' will directly call the taskletengine e.g. for std method calls from actors
        @appname e.g. system is 1e part of url which is routed http://localhost/appname/actor/method/
        @actor e.g. system is 2nd part of url which is routed http://localhost/appname/actor/method/
        @method e.g. "test" is part of url which is routed e.g. http://localhost/appname/actor/method/
        @paramvalidation e.g. {"name":"\w+","color":""}   the values are regexes
        @paramdescription is optional e.g. {"name":"this is the description for name"}
        @auth is for authentication if false then there will be no auth key checked

        example function called

            def test(self,webserver,path,params):
                return 'hello world!!'

            or without the self in the functioncall (when no class method)

            what you return is being send to the browser

        example call: http://localhost:9999/test?key=1234&color=dd&name=dd

        """

        appname = appname.replace("_", ".")
        actor = actor.replace("_", ".")
        method = method.replace("_", ".")
        self.app_actor_dict["%s_%s" % (appname, actor)] = 1

        methoddict = {'get': 'GET', 'set': 'PUT', 'new': 'POST', 'delete': 'DELETE',
                      'find': 'GET', 'list': 'GET', 'datatables': 'GET', 'create': 'POST'}
        self.routes["%s_%s_%s_%s" % ('GET', appname, actor, method)] = [function, paramvalidation, paramdescription, paramoptional, \
                                                                        description, auth, returnformat]

##################### SCHEDULING

    def _timer(self):
        """
        will remember time every 0.5 sec
        """
        lfmid = 0
        while True:
            self.epoch = int(time.time())
            if lfmid < self.epoch - 200:
                lfmid = self.epoch
                self.fiveMinuteId = j.base.time.get5MinuteId(self.epoch)
                self.hourId = j.base.time.getHourId(self.epoch)
                self.dayId = j.base.time.getDayId(self.epoch)
            gevent.sleep(0.5)

    def _minRepeat(self):
        while True:
            gevent.sleep(5)
            for key in self.schedule1min.keys():
                item, args, kwargs = self.schedule1min[key]
                item(*args, **kwargs)

    def _15minRepeat(self):
        while True:
            gevent.sleep(60 * 15)
            for key in self.schedule15min.keys():
                item, args, kwargs = self.schedule15min[key]
                item(*args, **kwargs)

    def _60minRepeat(self):
        while True:
            gevent.sleep(60 * 60)
            for key in self.schedule60min.keys():
                item, args, kwargs = self.schedule60min[key]
                item(*args, **kwargs)

    def getNow(self):
        return self.epoch

    def addSchedule1MinPeriod(self, name, method, *args, **kwargs):
        self.schedule1min[name] = (method, args, kwargs)

    def addSchedule15MinPeriod(self, name, method, *args, **kwargs):
        self.schedule15min[name] = (method, args, kwargs)

    def addSchedule60MinPeriod(self, name, method, *args, **kwargs):
        self.schedule60min[name] = (method, args, kwargs)

##################### START-STOP / get spaces/actors/buckets / addgreenlet

    def start(self):
        """
        Start the web server, serving the `routes`. When no `routes` dict is passed, serve a single 'test' route.

        This method will block until an exception stops the server.

        @param routes: routes to serve, will be merged with the already added routes
        @type routes: dict(string, list(callable, dict(string, string), dict(string, string)))
        """

        TIMER = gevent.greenlet.Greenlet(self._timer)
        TIMER.start()

        S1 = gevent.greenlet.Greenlet(self._minRepeat)
        S1.start()

        S2 = gevent.greenlet.Greenlet(self._15minRepeat)
        S2.start()

        S3 = gevent.greenlet.Greenlet(self._60minRepeat)
        S3.start()

        j.console.echo("webserver started on port %s" % self.port)
        self._webserver.serve_forever()

    def stop(self):
        self._webserver.stop()


    def getSpaces(self):
        return self.spacesloader.id2object.keys()

    def getBuckets(self):
        return self.bucketsloader.id2object.keys()

    def getActors(self):
        return self.actorsloader.id2object.keys()

    def getSpace(self, name, ignore_doc_processor=False):

        name = name.lower()
        if name not in self.spacesloader.spaces:
            raise RuntimeError("Could not find space %s" % name)
        space = self.spacesloader.spaces[name]
        if space.docprocessor == None and not ignore_doc_processor:
            space.loadDocProcessor()
        return space

    def loadSpace(self, name):
        space = self.getSpace(name)
        space.loadDocProcessor()
        return space

    def getBucket(self, name):
        if name not in self.bucketsloader.buckets:
            raise RuntimeError("Could not find bucket %s" % name)
        bucket = self.bucketsloader.buckets(name)
        return bucket


    def addGreenlet(self, appName, greenlet):
        """
        """
        greenletObject = greenlet()
        if greenletObject.method == "":
            raise RuntimeError("greenlet class needs to have a method")
        if greenletObject.actor == "":
            raise RuntimeError("greenlet class needs to have a actor")

        greenletObject.server = self
        self.addRoute(function=greenletObject.wscall,
                                appname=appName,
                                actor=greenletObject.actor,
                                method=greenletObject.method,
                                paramvalidation=greenletObject.paramvalidation,
                                paramdescription=greenletObject.paramdescription,
                                paramoptional=greenletObject.paramoptional,
                                description=greenletObject.description, auth=greenletObject.auth)

    def restartInProcess(self, app):
        import fcntl
        args = sys.argv[:]
        args.insert(0, sys.executable)
        apppath = j.system.fs.joinPaths(j.dirs.appDir, app)
        max_fd = 1024
        for fd in range(3, max_fd):
            try:
                flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            except IOError:
                continue
            fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
        os.chdir(apppath)
        os.execv(sys.executable, args)

    def __str__(self):
        out=""
        for key,val in self.__dict__.iteritems():
            if key[0]<>"_" and key not in ["routes"]:
                out+="%-35s :  %s\n"%(key,val)
        routes=",".join(self.routes.keys())
        out+="%-35s :  %s\n"%("routes",routes)
        items=out.split("\n")
        items.sort()
        out="portalserver:"+"\n".join(items)
        return out

    __repr__ = __str__


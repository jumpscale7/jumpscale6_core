import re
import urlparse
import pprint
import os

from beaker.middleware import SessionMiddleware

from OpenWizzy import o
from gevent.pywsgi import WSGIServer
import gevent
import time

from MacroExecutor import MacroExecutorPage, MacroExecutorWiki, MacroExecutorPreprocess
import mimeparse

BLOCK_SIZE = 4096

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_JS = 'application/javascript'
CONTENT_TYPE_YAML = 'application/yaml'
CONTENT_TYPE_PLAIN = 'text/plain'
CONTENT_TYPE_HTML = 'text/html'


class GeventWebserverFactory:
    def get(self, port, secret, wwwroot="", filesroot="", cfgdir=""):
        return GeventWebserver(port, secret, wwwroot=wwwroot, filesroot=filesroot, cfgdir=cfgdir)

    def getClient(self, ip, port, secret):
        return GeventWSClient(ip, port, secret)

    def getMacroExecutors(self):
        return (MacroExecutorPreprocess, MacroExecutorPage, MacroExecutorWiki)


class GeventWSClient():
    def __init__(self, ip, port, secret=None):
        self.ip = ip
        self.port = port
        self.secret = secret
        self.httpconnection = o.clients.http.getConnection()

    def html2text(self, data):
        # get only the body content
        bodyPat = re.compile(r'< body[^<>]*?>(.*?)< / body >', re.I)
        result = re.findall(bodyPat, data)
        if len(result) > 0:
            data = result[0]

        # now remove the java script
        p = re.compile(r'< script[^<>]*?>.*?< / script >')
        data = p.sub('', data)

        # remove the css styles
        p = re.compile(r'< style[^<>]*?>.*?< / style >')
        data = p.sub('', data)

        # remove html comments
        p = re.compile(r'')
        data = p.sub('', data)

        # remove all the tags
        p = re.compile(r'<[^<]*?>')
        data = p.sub('', data)

        data = data.replace("&nbsp;", " ")
        data = data.replace("\n\n", "\n")

        return data

    def ping(self, nrping=1):
        url = "http://%s:%s/ping/" % (self.ip, self.port)
        for nr in range(nrping):
            result = self.httpconnection.get(url)
            result = result.read()
            if result != "ping":
                raise RuntimeError("ping error to %s %s" % (self.ip, self.port))

    def callWebService(self, appname, actorname, method, **params):
        """
        ip,port & secret are params of webservice to call
        @params the extra params is what will be passed to the webservice as arguments
            e.g. name="kds",color="red"
        @return 0, result #if ok
        @return 1, result #if error
        @return 3, result #if asyncresult
        """

        url = "http://%s:%s/restmachine/%s/%s/%s?authkey=%s" % (self.ip, self.port, appname, actorname, method, self.secret)
        o.logger.log("Calling URL %s" % url, 8)
        if "params" in params:
            for key in params["params"]:
                params[key] = params["params"][key]
            params.pop("params")
        #params["caller"] = o.core.grid.config.whoami
        data = o.db.serializers.getSerializerType('j').dumps(params)

        headers = {'content-type': 'application/json'}

        result = self.httpconnection.post(url, headers=headers, data=data)

        contentType = result.headers['Content-Type']
        content = result.read()

        # o.logger.log("Received result %s" % content, 8)

        if contentType == CONTENT_TYPE_JSON:
            decodedResult = o.db.serializers.getSerializerType('j').loads(content)
        else:
            raise ValueError("Cannot handle content type %s" % contentType)

        if isinstance(decodedResult, basestring):
            if decodedResult.find("ERROR: PLEASE SPECIFY PARAM") != -1:
                raise RuntimeError(self.html2text(decodedResult))
            elif decodedResult.startswith("ASYNC::"):
                r = int(decodedResult.split("::", 1)[1])
                return 3, r
            elif decodedResult.startswith("ERRORJSON::"):
                r = decodedResult.split("\n", 1)[1]  # remove first line
                return 1, o.db.serializers.getSerializerType('j').loads(r)
            elif decodedResult.startswith("ERROR::"):
                raise RuntimeError("ERROR SHOULD HAVE BEEN IN JSON FORMAT.\n%s"%self.html2text(decodedResult))

        return 0, decodedResult


class RequestContext(object):
    """
    is context of one request to WS
    please keep this as light as possible because these objects are mostly created
    """
    def __init__(self, application, actor, method, env, start_response, path, params={}, fformat=""):
        self.env = env
        self._start_response = start_response
        if params == "":
            params = {}
        self.params = params
        self.path = path
        self.actor = actor
        self.application = application
        self.method = method
        self._response_started = False
        self.fformat = fformat.strip().lower()

    def start_response(self, *args, **kwargs):
        if self._response_started:
            print 'RESPONSE Already started ignoring'
            return
        self._response_started = True
        return self._start_response(*args, **kwargs)

    def checkFormat(self):
        if self.fformat == "" or self.fformat == None:
            self.fformat = "json"
        if self.fformat not in ["human", "json", "jsonraw", "text", "html", "raw"]:
            return False
        return True


class GeventWebserver:
    def __init__(self, port, secret, wwwroot="", filesroot="", cfgdir=""):
        self.port = int(port)
        self.secret = secret
        self.app_actor_dict = {}
        self.epoch = 0
        self.contentdirs = {}
        self.cfgdir = cfgdir
        self.libpath = o.html.getHtmllibDir()
        self.logdir = o.system.fs.joinPaths(o.dirs.varDir, "qwiki", "logs")
        o.system.fs.createDir(self.logdir)
        # o.errorconditionhandler.setExceptHook()
        self.userKeyToName = {}

        session_opts = {
            'session.cookie_expires': False,
            'session.type': 'file',
            'session.data_dir': '%s'%o.system.fs.joinPaths(o.dirs.varDir, "beakercache")
        }
        self.router = SessionMiddleware(self.router, session_opts)
        self.webserver = WSGIServer(('127.0.0.1', self.port), self.router)

        wwwroot = wwwroot.replace("\\", "/")
        while len(wwwroot) > 0 and wwwroot[-1] == "/":
            wwwroot = wwwroot[:-1]

        self.wwwroot = wwwroot
        self.filesroot = filesroot
        self.confluence2htmlconvertor = o.tools.docgenerator.getConfluence2htmlConvertor()

        self.schedule1min = {}
        self.schedule15min = {}
        self.schedule60min = {}

        self._init()

    def _init(self):

        self.pageKey2doc = {}
        self.routes = {}
        self.routesext = {}
        self.bucketsloader = o.core.portalloader.getBucketsLoader()
        self.spacesloader = o.core.portalloader.getSpacesLoader()

        macroPathsPreprocessor = ["system/system__contentmanager/macros/preprocess"]
        macroPathsWiki = ["system/system__contentmanager/macros/wiki"]
        macroPathsPage = ["system/system__contentmanager/macros/page"]

        self.macroexecutorPreprocessor = MacroExecutorPreprocess(macroPathsPreprocessor)
        self.macroexecutorPage = MacroExecutorPage(macroPathsPage)
        self.macroexecutorWiki = MacroExecutorWiki(macroPathsWiki)

        self.initGeoIP()

    def initGeoIP(self):
        try:
            import GeoIP
            self.geoIP = GeoIP.open("/opt/GeoLiteCity.dat", GeoIP.GEOIP_STANDARD)
        except:
            self.geoIP = None

    def getpage(self):
        page = o.tools.docgenerator.pageNewHTML("index.html", htmllibPath="/lib")
        return page

    def sendpage(self, page, start_response):
        contenttype = "text/html"
        start_response('200 OK', [('Content-Type', contenttype), ])
        return [page.getContent()]

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
            groupsusers = o.apps.system.usermanager.getusergroups(username)
            if groupsusers != None:
                # groupsusers+=[username]  #@todo why did we do that???, maybe something will break now
                pass
            else:
                print "ERROR:  user %s has no groups" % username

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
        if right == "*":
            right = "rwa"
        print "right:%s" % right
        return username, right

    def unloadActorFromRoutes(self, appname, actorname):
        for key in self.routes.keys():
            appn, actorn, remaining = key.split("_", 2)
            # print appn+" "+appname+" "+actorn+" "+actorname
            if appn == appname and actorn == actorname:
                self.routes.pop(key)

    def getDoc(self, space, name, ctx, params={}):
        print "getdoc:%s"%space
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
                spaceObject.loadDocProcessor()  # dynamic load of space

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

        return doc, params

    def log(self, ctx, user, path, space="", pagename=""):
        path2 = o.system.fs.joinPaths(self.logdir, "user_%s.log" % user)

        epoch = o.base.time.getTimeEpoch()+3600*6
        hrtime = o.base.time.epoch2HRDateTime(epoch)

        if False and self.geoIP != None:  # @todo fix geoip, also make sure nginx forwards the right info
            ee = self.geoIP.record_by_addr(ctx.env["REMOTE_ADDR"])
            loc = "%s_%s_%s" % (ee["area_code"], ee["city"], ee["region_name"])
        else:
            loc = ""

        msg = "%s|%s|%s|%s|%s|%s|%s\n" % (hrtime, ctx.env["REMOTE_ADDR"], epoch, space, pagename, path, loc)
        o.system.fs.writeFile(path2, msg, True)

        if space != "":
            msg = "%s|%s|%s|%s|%s|%s|%s\n" % (hrtime, ctx.env["REMOTE_ADDR"], epoch, user, pagename, path, loc)
            pathSpace = o.system.fs.joinPaths(self.logdir, "space_%s.log" % space)
            o.system.fs.writeFile(pathSpace, msg, True)

    def startSession(self, ctx, path):
        session = ctx.env['beaker.session']
        if "authkey" in ctx.params:
            # user is authenticated by a special key
            key = ctx.params["authkey"]
            if key in self.userKeyToName:
                username = self.userKeyToName[key]
                session['user'] = username
                session.save()
            elif key == self.secret:
                session['user'] = 'admin'
                session.save()
            else:
                #check if authkey is a session
                newsession = session.get_by_id(key)
                if newsession:
                    session = newsession
                    ctx.env['beaker.session'] = session
                else:
                    ctx.start_response('419 Authentication Timeout', [])
                    return False, [str(self.returnDoc(ctx, ctx.start_response, "system", "accessdenied", extraParams={"path": path}))]

        if "user_logoff_" in ctx.params:
            session.delete()
            session.save()

        if "user_login_" in ctx.params:
            # user has filled in his login details, this is response on posted info
            name = ctx.params['user_login_']
            secret = ctx.params['passwd']
            if o.apps.system.usermanager.authenticate(name, secret):
                session['user'] = name
                if "querystr" in session:
                    ctx.env['QUERY_STRING'] = session['querystr']
                else:
                    ctx.env['QUERY_STRING'] = ""
                session.save()
                #user is loging in from login page redirect him to home
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



    def router(self, environ, start_response):
        path = environ["PATH_INFO"].lstrip("/")
        path = path.replace("wiki/wiki", "wiki")
        if path == "" or path.rstrip("/") == "wiki":
            path == "wiki/system"
        print "path:%s"%path

        if path.find("favicon.ico") != -1:
            return self.processor_page(environ, start_response, self.filesroot, "favicon.ico", prefix="")

        ctx = RequestContext(application="", actor="", method="", env=environ,
                             start_response=start_response, path=path, params=None)
        ctx.params = self._getParamsFromEnv(environ, ctx)

        if path.find("images/") == 0:
            path = path[8:]
            space, image = path.split("/", 1)
            spaceObject = self.getSpace(space)
            image = image.lower()
            if image in spaceObject.docprocessor.images:
                path = spaceObject.docprocessor.images[image]
                return self.processor_page(environ, start_response, o.system.fs.getDirName(path), o.system.fs.getBaseName(path), prefix="images")
            ctx.start_response('404', [])

        if path.find("files/specs/") == 0:
            path = path[6:]
            user = "None"
            self.log(ctx, user, path)
            return self.processor_page(environ, start_response, self.filesroot, path, prefix="files/")

        if path.find(".files") != -1:
            user = "None"
            self.log(ctx, user, path)
            space = path.split("/")[1].lower()
            path = "/".join(path.split("/")[3:])
            sploader = self.spacesloader.getSpaceFromId(space)
            filesroot = o.system.fs.joinPaths(sploader.model.path, ".files")
            return self.processor_page(environ, start_response, filesroot, path, prefix="")

        # user is logged in now
        is_session, session = self.startSession(ctx, path)
        if not is_session:
            return session
        user = session['user']


        if path.startswith("restmachine/"):
            path = path[12:]
            return self.processor_rest(environ, start_response, path, human=False, ctx=ctx)

        if path.find("restextmachine/") == 0:
            path = path[15:]
            return self.processor_restext(environ, start_response, path, human=False, ctx=ctx)


        if path.find("wiki") == 0:
            # is page in wiki
            path = path[5:].strip("/")

            space, pagename = self.path2spacePagename(path)
            self.log(ctx, user, path, space, pagename)
            return [str(self.returnDoc(ctx, start_response, space, pagename, {}))]

        elif path.find("rest/") == 0:
            path = path[5:]
            space, pagename = self.path2spacePagename(path.strip("/"))
            self.log(ctx, user, path, space, pagename)
            return self.processor_rest(environ, start_response, path, ctx=ctx)

        elif path.find("restext/") == 0:
            path = path[8:]
            space, pagename = self.path2spacePagename(path.strip("/"))
            self.log(ctx, user, path, space, pagename)
            return self.processor_restext(environ, start_response, path,
                                          ctx=ctx)

        elif path.find("ping/") == 0:
            status = '200 OK'
            headers = [
                ('Content-Type', "text/html"),
            ]
            start_response(status, headers)
            return ["ping"]

        elif path.find("files/") == 0:
            path = path[6:]
            self.log(ctx, user, path)
            return self.processor_page(environ, start_response, self.filesroot, path, prefix="files")

        elif path.find("specs/") == 0:
            path = path[6:]
            return self.processor_page(environ, start_response, "specs", path, prefix="specs")
        elif path.find("appservercode/") == 0:
            path = path[14:]
            return self.processor_page(environ, start_response, "code", path, prefix="code", webprefix="appservercode")
        elif path.find("lib/") == 0:
            path = path[4:]
            return self.processor_page(environ, start_response, self.libpath, path, prefix="", webprefix="lib", index=False)
        else:
            ctx.params["path"] = path
            return [str(self.returnDoc(ctx, start_response, "system", "PageNotFound"))]

    def returnDoc(self, ctx, start_response, space, docname, extraParams={}):
        doc, params = self.getDoc(space, docname, ctx, params=ctx.params)

        if doc.dirty or "reload" in ctx.params:
            doc.loadFromDisk()
            doc.preprocess()

        ctx.params.update(extraParams)

        # doc.applyParams(ctx.params)
        content, doc = doc.executeMacrosDynamicWiki(paramsExtra=extraParams, ctx=ctx)

        content, page = self.confluence2htmlconvertor.convert(content, doc=doc, requestContext=ctx, page=self.getpage(), paramsExtra=ctx.params)

        if not 'postprocess' in page.processparameters or page.processparameters['postprocess']:
            page.body = page.body.replace("$$space", space)
            page.body = page.body.replace("$$page", doc.name)
            page.body = page.body.replace("$$path", doc.path)

        page.body = page.body.replace("$$$menuright", "")

        if "todestruct" in doc.__dict__:
            doc.destructed = True

        start_response('200 OK', [('Content-Type', "text/html"), ])
        return page

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
            content = o.system.fs.fileGetContents(path)
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
            while path.find(webprefix+"/") == 0:
                path = path[len(webprefix)+1:]
            while path.find(prefix+"/") == 0:
                path = path[len(prefix)+1:]
            return path

        def send_file(file_path, size):
            # print "sendfile:%s" % path
            f = open(file_path, "rb")
            block = f.read(BLOCK_SIZE*10)
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
            pathfull = wwwroot+"/"+path

        else:
            pathfull = path

        contenttype = "text/html"
        content = ""

        if path == "favicon.ico":
            pathfull = "wiki/System/favicon.ico"

        if not o.system.fs.exists(pathfull):
            print "error"
            headers = [('Content-Type', contenttype), ]
            start_response("404 Not found", headers)
            return ["path %s not found" % path]

        ext = path.split(".")[-1].lower()
        size = os.path.getsize(pathfull)

        if ext == "html":
            contenttype = "text/html"
        elif ext == "wiki":
            contenttype = "text/html"
            # return formatWikiContent(pathfull,start_response)
            return formatContent(contenttype, pathfull, "python", start_response)
        elif ext == "py":
            contenttype = "text/html"
            return formatContent(contenttype, pathfull, "python", start_response)
        elif ext == "jpg" or ext == "jpeg":
            contenttype = "image/jpeg"
        elif ext == "png":
            contenttype = "image/png"
        elif ext == "gif":
            contenttype = "image/gif"
        elif ext == "ico":
            contenttype = "image/ico"
        elif ext == "css":
            contenttype = "text/css"
        elif ext == "spec":
            contenttype = "text/html"
            return formatContent(contenttype, pathfull, "python", start_response)
        elif ext == "js":
            contenttype = "application/x-javascript"
        else:
            contenttype = "binary/octet-stream"
        # print contenttype

        status = '200 OK'

        headers = [
            ('Content-Type', contenttype),
            ("Content-length", str(size)),
        ]

        start_response(status, headers)

        if content != "":
            return [content]
        else:
            return send_file(pathfull, size)

    def validate(self, restext, auth, ctx):
        if ctx.params == "":
            msg = 'No parameters given to actormethod.'
            return False, msg
        if auth and ctx.env['beaker.session']['user'] == 'guest':
            msg = 'NO VALID AUTHORIZATION KEY GIVEN, use get param called key (check key probably auth error).'
            ctx.start_response('401 %s' % msg, [])
            return False, msg

        if restext:
            paramCriteria = self.routesext[ctx.path][1]
            paramOptional = self.routesext[ctx.path][3]
        else:
            paramCriteria = self.routes[ctx.path][1]
            paramOptional = self.routes[ctx.path][3]
        for key in paramCriteria.keys():
            criteria = paramCriteria[key]
            if key not in ctx.params:
                if key in paramOptional:
                    # means is optional
                    ctx.params[key] = None
                else:
                    message = 'get param with name:%s is missing.' % key
                    return False, message
            elif (criteria != "" and ctx.params[key] == "")\
                    or (criteria != "" and not o.codetools.regex.matchAllText(criteria, ctx.params[key])):
                msg = 'value of param %s not correct needs to comform to regex %s'%(key, criteria)
                return False, msg
        return True, ""

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
                postParams = o.db.serializers.getSerializerType('j').loads(postData)
                if postParams:
                    params.update(postParams)
                return params
            elif env['CONTENT_TYPE'].find("www-form-urlencoded") != -1:
                params.update(dict(urlparse.parse_qsl(postData)))
                return params
            else:
                self.raiseError(ctx, "Could not deserialize posted information, only application/json format supported")
        return params

    def _getActorMethodCall(self, appname, actor, method):
        """
        used for during error show links to methods in browser
        """
        url = "/rest/%s/%s/%s?" % (appname, actor, method)

        auth = self.routes["%s_%s_%s" % (appname, actor, method)][5]
        if auth:
            params = ["authkey"]
        else:
            params = []
        params.extend(self.routes["%s_%s_%s" % (appname, actor, method)][1].keys())

        for param in params:
            url += "%s=&"%param
        url += "format=text"
        if url[-1] == "&":
            url = url[:-1]
        if url[-1] == "?":
            url = url[:-1]
        # url="<a href=\"%s\">%s</a> " % (url,url)
        return url

    def _getActorInfoUrl(self, appname, actor):
        """
        used for during error show links to actor in browser
        """
        if actor == "":
            url = "/rest/%s/" % (appname)
        else:
            url = "/rest/%s/%s/" % (appname, actor)
        # url="<a href=\"%s\">go here for more info about actor %s in %s</a> " % (url,actor,appname)
        return url

    def getServiceInfo(self, appname, actorname, methodname, page=None):
        """
        used for during error show info about 1 actor
        """
        if appname == "" or actorname == "" or methodname == "":
            txt = "getServiceInfo need 4 params: ctx,appname, actorname, methoname, got: ?,%s, %s,%s" % (appname, actorname, methodname)
            return txt
        if page == None:
            page = self.getpage()
        page.addHeading("%s.%s.%s" % (appname, actorname, methodname), 5)

        url = self._getActorMethodCall(appname, actorname, methodname)

        routeData = self.routes["%s_%s_%s" % (appname, actorname, methodname)]
        # routedata: function,paramvalidation,paramdescription,paramoptional,description
        description = routeData[4]
        if description.strip() != "":
            page.addMessage(description)
        # param info
        params = routeData[1]
        descriptions = routeData[2]
        # optional = routeData[3]
        page.addLink("%s" % (methodname), url)
        if len(params.keys()) > 0:
            page.addBullet("Params:\n", 1)
            for key in params.keys():
                if key in descriptions:
                    descr = descriptions[key].strip()
                else:
                    descr = ""
                page.addBullet("- %s : %s \n" % (key, descr), 2)

        return page

    def getServicesInfo(self, appname="", actor="", page=None, extraParams={}):
        """
        used for during error show info about all services
        """
        actorsloader = o.core.portal.runningPortal.actorsloader
        if appname != "" and actor != "":
            result = o.core.portal.runningPortal.activateActor(appname, actor)
            if result == False:
                # actor was not there
                page = self.getpage()
                page.addHeading("Could not find actor %s %s."%(appname, actor), 4)
                return page

        if page == None:
            page = self.getpage()
        if appname == "":
            page.addHeading("Applications in appserver.", 4)
            appnames = {}

            for appname, actorname in actorsloader.getAppActors():  # [item.split("_", 1) for  item in self.app_actor_dict.keys()]:
                appnames[appname] = 1
            appnames = appnames.keys()
            appnames.sort()
            for appname in appnames:
                link = page.getLink("%s" % (appname), self._getActorInfoUrl(appname, ""))
                page.addBullet(link)
            return page

        if actor == "":
            page.addHeading("Actors for application %s" % (appname), 4)
            actornames = []
            for appname2, actorname2 in actorsloader.getAppActors():  # [item.split("_", 1) for  item in self.app_actor_dict.keys()]:
                if appname2 == appname:
                    actornames.append(actorname2)
            actornames.sort()

            for actorname in actornames:
                link = page.getLink("%s" % (actorname), self._getActorInfoUrl(appname, actorname))
                page.addBullet(link)
            return page

        keys = self.routes.keys()
        keys.sort()
        page.addHeading("list", 2)
        for item in keys:
            app2, actor2, method = item.split("_")
            if app2 == appname and actor2 == actor:
                url = self._getActorMethodCall(appname, actor, method)
                link = page.getLink(item, url)
                page.addBullet(link)

        page.addHeading("details", 2)
        for item in keys:
            app2, actor2, method = item.split("_")
            if app2 == appname and actor2 == actor:
                page = self.getServiceInfo(appname, actor, method, page=page)
        return page

    def raiseError(self, ctx, msg="", msginfo="", errorObject=None, httpcode="500 Internal Server Error"):
        """
        """
        if not ctx.checkFormat():
            # error in format
            eco = o.errorconditionhandler.getErrorConditionObject()
            eco.errormessage = "only format supported = human or json, format is put with param &format=..."
            eco.type = "WRONGINPUT"
            print "WRONG FORMAT"
        else:
            if errorObject != None:
                eco = errorObject
            else:
                eco = o.errorconditionhandler.getErrorConditionObject()

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

        if eco.type == "":
            eco.type = "WSERROR"

        o.errorconditionhandler.processErrorConditionObject(eco)

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
            msg = o.db.serializers.getSerializerType('j').dumps(todict(eco))

        ctx.start_response(httpcode, [('Content-Type', 'text/html')])

        o.console.echo("***ERROR***:%s : method %s from ip %s with params %s" % (
            msg, scriptName, remoteAddress, queryString), 2)

        return msg

    def _text2html(self, text):
        text = text.replace("\n", "<br>")
        # text=text.replace(" ","&nbsp; ")
        return text

    def _text2htmlSerializer(self, content):
        return self._text2html(pprint.pformat(content))

    def _resultjsonSerializer(self, content):
        return o.db.serializers.getSerializerType('j').dumps({"result":content})

    def _resultyamlSerializer(self, content):
        return o.code.object2yaml({"result":content})

    def getMimeType(self, contenttype, format_types):
        CONTENT_TYPES = {
    "application/json":o.db.serializers.getSerializerType('j').dumps,
    "application/yaml":self._resultyamlSerializer,
    "text/plain":str,
    "text/html":self._text2htmlSerializer
    }

        if not contenttype:
            serializer = format_types["text"]["serializer"]
            return CONTENT_TYPE_HTML, serializer
        else:
            mimeType = mimeparse.best_match(CONTENT_TYPES.keys(), contenttype)
            serializer = CONTENT_TYPES[mimeType]
            return mimeType, serializer



    def reformatOutput(self, ctx, result, restreturn=False):
        FFORMAT_TYPES = {
    "text": {"content_type":CONTENT_TYPE_HTML, "serializer": self._text2htmlSerializer},
    "raw": {"content_type": CONTENT_TYPE_PLAIN, "serializer": str},
    "jsonraw": {"content_type": CONTENT_TYPE_JSON, "serializer": o.db.serializers.getSerializerType('j').dumps},
    "json": {"content_type": CONTENT_TYPE_JSON, "serializer": self._resultjsonSerializer},
    "yaml": {"content_type": CONTENT_TYPE_YAML, "serializer": self._resultyamlSerializer}
    }

        fformat = ctx.fformat
        if '_jsonp' in ctx.params:
            return CONTENT_TYPE_JS, "%s(%s);" % (ctx.params['_jsonp'], o.db.serializers.getSerializerType('j').dumps(result))

        if "CONTENT_TYPE" not in ctx.env:
            ctx.env['CONTENT_TYPE'] = CONTENT_TYPE_PLAIN

        if ctx.env['CONTENT_TYPE'].find("form-") != -1:
            ctx.env['CONTENT_TYPE'] = CONTENT_TYPE_PLAIN
        # normally HTTP_ACCEPT defines the return type we should rewrite this
        if fformat:
            #extra format paramter overrides http_accept header
            return FFORMAT_TYPES[fformat]['content_type'], FFORMAT_TYPES[fformat]['serializer'](result)
        else:
            if 'HTTP_ACCEPT' in ctx.env:
                returntype = ctx.env['HTTP_ACCEPT']
            else:
                returntype = ctx.env['CONTENT_TYPE']
            content_type, serializer = self.getMimeType(returntype, FFORMAT_TYPES)
            return content_type, serializer(result)

    def processor_restext(self, env, start_response, path, human=True, ctx=False):
        if ctx == False:
            raise RuntimeError("ctx cannot be empty")
        try:
            o.logger.log("Routing request to %s" % path, 5)

            def respond(contentType, msg):
                if contentType:
                    start_response('200 OK', [('Content-Type', contentType)])
                return msg

            success, message, params = self.restPathProcessor(path)
            if not success:
                params["error"] = message
                if human:
                    page = self.returnDoc(ctx, start_response, "system", "rest",
                        extraParams = params)
                    return [str(page)]
                else:
                    return self.raiseError(ctx, message)
            paths = params['paths']
            appname = paths[0]
            actor = paths[1]
            actorfunction = None
            subobject = False
            getfind = False
            getdatatables = False
            if len(ctx.params) > 0:
                if 'query' in ctx.params:
                    getfind = True
                elif 'datatables' in ctx.params:
                    getdatatables = True
            if len(paths) == 2:
                # we have only a actor function
                if 'function' in ctx.params:
                    actorfunction = ctx.params.pop('function')
            requestmethod = ctx.env['REQUEST_METHOD']
            if len(paths) > 2:
                modelgroup = paths[2]
            if len(paths) > 3:
                objectid = paths[3]
                ctx.params['id'] = objectid
                subobject = True
            if actorfunction:
                routekey = "%s_%s_%s_%s" % (requestmethod, appname, actor,
                                            actorfunction)
            else:
                if requestmethod == 'GET':
                    if subobject:
                        routekey = "%s_%s_%s_%s_get" % (requestmethod, appname, actor,
                                                        modelgroup)
                    elif getfind:
                        routekey = "%s_%s_%s_%s_find" % (requestmethod,
                                                         appname, actor, modelgroup)
                    elif getdatatables:
                        routekey = "%s_%s_%s_%s_datatables" % (requestmethod,
                                                               appname, actor, modelgroup)
                    else:
                        routekey = "%s_%s_%s_%s_list" % (requestmethod,
                                                         appname, actor, modelgroup)

                elif requestmethod == 'OPTIONS':
                    result = 'Allow: HEAD,GET,PUT,DELETE,OPTIONS'
                    contentType, result = self.reformatOutput(ctx, result)
                    return respond(contentType, result)

                else:
                    routekey = "%s_%s_%s_%s" % (requestmethod,
                                                appname, actor, modelgroup)
            success, ctx, result = self.restRouter(env, start_response, path, paths, ctx, True, routekey, human)
            if not success:
                return result
            success, result = self.execute_rest_call(ctx, result, True)
            if not success:
                return result

            if human:
                ctx.format = "json"
                params = {}
                params["result"] = result
                return [str(self.returnDoc(ctx, start_response, "system", "restresult", extraParams=params))]
            else:
                contentType, result = self.reformatOutput(ctx, result)
                return respond(contentType, result)
        except Exception, errorObject:
            eco = o.errorconditionhandler.parsePythonErrorObject(errorObject)
            if ctx == False:
                print "NO webserver context yet, serious error"
                o.errorconditionhandler.processErrorConditionObject(eco)
                print eco
            else:
                return self.raiseError(ctx, errorObject=eco)


    def restPathProcessor(self, path):
        """
        Function which parse a path, returning True or False depending on
        successfull parsing, a error message and a dict of parameters.
        When successfull the params dict contains the path elements otherwise it
        contains if provided the actorname  and appname.
        """
        o.logger.log("Process path %s" % path, 5)
        params = {}
        while path != "" and path[0] == "/":
            path = path[1:]
        while path != "" and path[-1] == "/":
            path = path[:-1]
        if path.strip() == "":
            return (False, "Bad input path was empty. Format of url need to be http://$ipaddr/rest/$appname/$actorname/$actormetho?...", {})
        paths = path.split("/")
        if len(paths) < 3:
            msginfo = "Format of url need to be http://$ipaddr/rest/$appname/$actorname/$actormethod?...\n\n"
            if len(paths) > 0:
                appname = paths[0]
            else:
                appname = ""
                actor = ""
            if len(paths) > 1:
                actor = paths[1]
            else:
                actor = ""
            params["appname"]  =  appname
            params["actorname"] = actor
            return (False, msginfo, params)
        params["paths"] = paths
        return (True, "", params)

    def restRouter(self, env, start_response, path, paths, ctx, ext=False, routekey=None, human=False):
        """
        """
        if not routekey:
            routekey = "%s_%s_%s" % (paths[0], paths[1], paths[2])
        o.logger.log("Execute %s %s" % (env["REMOTE_ADDR"], routekey))
        if ext:
            routes = self.routesext
        else:
            routes = self.routes
        if routekey in routes:
            if human:
                ctx.fformat = "human"
            elif("format" not in ctx.params):
                ctx.fformat = routes[routekey][6]
            else:
                ctx.fformat = ctx.params["format"]
            ctx.path = routekey
            ctx.fullpath = path
            ctx.application = paths[0]
            ctx.actor = paths[1]
            ctx.method = paths[2]
            auth = routes[routekey][5]
            resultcode, msg = self.validate(ext, auth, ctx)
            if resultcode == False:
                if human:
                    params = {}
                    params["error"] =  "Incorrect Request: %s" % msg
                    params["appname"] = ctx.application
                    params["actorname"] = ctx.actor
                    params["method"] = ctx.method
                    page = self.returnDoc(ctx, start_response, "system",
                    "restvalidationerror", extraParams=params)
                    return (False, ctx, [str(page)])
                else:
                    return (False, ctx, self.raiseError(ctx, msg))
            else:
                return (True, ctx, routekey)
        else:
            msg = "Could not find method, path was %s" % (path)
            appname = paths[0]
            actor = paths[1]
            page = self.getServicesInfo(appname, actor)
            return (False, ctx, self.raiseError(ctx=ctx, msg=msg,
                msginfo=str(page)))


    def execute_rest_call(self, ctx, routekey, ext=False):
        if ext:
            routes = self.routesext
        else:
            routes = self.routes
        try:
            method = routes[routekey][0]
            result = method(ctx=ctx, **ctx.params)
            return (True, result)
        except Exception, errorObject:
            eco = o.errorconditionhandler.parsePythonErrorObject(errorObject)
            msg = "Execute method %s failed." % (routekey)
            return (False, self.raiseError(ctx=ctx, msg=msg, errorObject=eco))

    def processor_rest(self, env, start_response, path, human=True, ctx=False):
        if ctx == False:
            raise RuntimeError("ctx cannot be empty")
        try:
            o.logger.log("Routing request to %s" % path, 5)

            def respond(contentType, msg):
                # o.logger.log("Responding %s" % msg, 5)
                if contentType:
                    ctx.start_response('200 OK', [('Content-Type', contentType)])
                print msg
                return msg

            success, msg, params = self.restPathProcessor(path)
            if not success:
                params["error"] = msg
                if human:
                    page = self.returnDoc(ctx, start_response, "system", "rest",
                        extraParams = params)
                    return [str(page)]
                else:
                    return self.raiseError(ctx, msg)
            paths = params['paths']

            success, ctx, result = self.restRouter(env, start_response, path,
                    paths, ctx, human = human)
            if not success:
                return result
            success, result = self.execute_rest_call(ctx, result)
            if not success:
                return result

            if human:
                ctx.format = "json"
                params = {}
                params["result"] = result
                return [str(self.returnDoc(ctx, start_response, "system", "restresult", extraParams=params))]
            else:
                contentType, result = self.reformatOutput(ctx, result)
                return [respond(contentType, result)]
        except Exception, errorObject:
            eco = o.errorconditionhandler.parsePythonErrorObject(errorObject)
            if ctx == False:
                print "NO webserver context yet, serious error"
                o.errorconditionhandler.processErrorConditionObject(eco)
                print eco
            else:
                return self.raiseError(ctx, errorObject=eco)

    def test(self, ctx, path, params):
        return 'hello world!!'

    def addExtRoute(self, function, appname, actor, method, actorobjects, paramvalidation={}, paramdescription={}, paramoptional={}, description="", auth=True, returnformat=None):
        """
        @param function is the function which will be called as follows: function(webserver,path,params):
            function can also be a string, then only the string will be returned
            if str=='taskletengine' will directly call the taskletengine e.g. for std method calls from actors
        @appname e.g. system is 1e part of url which is routed http://localhost/appname/actor/method/
        @actor e.g. system is 2nd part of url which is routed http://localhost/appname/actor/method/
        @method e.g. "test" is part of url which is routed e.g. http://localhost/appname/actor/method/
        @actorobjects: all existing object groups of this actor, this to create
        the different api calls
        @paramvalidation e.g. {"name":"\w+","color":""}   the values are regexes
        @paramdescription is optional e.g. {"name":"this is the description for name"}
        @auth is for authentication if false then there will be no auth key checked

        example object 'user' and usercreate function

        example call: http://localhost:9999/test?key=1234&color=dd&name=dd
        """

        appname = appname.replace("_", ".")
        actor = actor.replace("_", ".")
        method = method.replace("_", ".")
        # first check if the function is a default CRUD action on a existing
        # object
        methoddict = {'get': 'GET', 'set': 'PUT', 'new': 'POST', 'delete': 'DELETE',
                      'find': 'GET', 'list': 'GET', 'datatables': 'GET', 'create': 'POST'}
        if method.find('model.') == 0:
            # this is a model function, eg model_object_get ...
            methodparts = method.split('.')
            objectname = methodparts[1]
            possiblemethod = methodparts[2]
            requesttype = methoddict[possiblemethod]
            if possiblemethod == 'list':
                self.routesext["%s_%s_%s_%s_list" % (requesttype, appname, actor, objectname)] = [function, paramvalidation,
                                                                                                  paramdescription, paramoptional, description, auth, returnformat]
                return
            elif possiblemethod == 'get':
                self.routesext["%s_%s_%s_%s_get" % (requesttype, appname, actor, objectname)] = [function, paramvalidation,
                                                                                                 paramdescription, paramoptional, description, auth, returnformat]
                return
            elif possiblemethod == 'find':
                self.routesext["%s_%s_%s_%s_find" % (requesttype, appname, actor, objectname)] = [function, paramvalidation,
                                                                                                  paramdescription, paramoptional, description, auth, returnformat]
            elif possiblemethod == "datatables":
                self.routesext["%s_%s_%s_%s_datatables" % (requesttype, appname, actor, objectname)] = [function, paramvalidation,
                                                                                                        paramdescription, paramoptional, description, auth, returnformat]
                return
            else:
                self.routesext["%s_%s_%s_%s" % (requesttype, appname, actor,
                                                objectname)] = [function, paramvalidation, paramdescription, paramoptional, description, auth, returnformat]
                return
        self.routesext["%s_%s_%s_%s" % ('GET', appname, actor, method)] = [function, paramvalidation, paramdescription, paramoptional, description,
                                                                           auth, returnformat]
        return

    def addRoute(self, function, appname, actor, method, paramvalidation={}, paramdescription={}, paramoptional={}, description="", auth=True, returnformat=None):
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
        self.routes["%s_%s_%s" % (appname, actor, method)] = [function, paramvalidation, paramdescription, paramoptional, description, auth, returnformat]

    def _timer(self):
        """
        will remember time every 0.5 sec
        """
        lfmid = 0
        while True:
            self.epoch = int(time.time())
            if lfmid < self.epoch-200:
                lfmid = self.epoch
                self.fiveMinuteId = o.base.time.get5MinuteId(self.epoch)
                self.hourId = o.base.time.getHourId(self.epoch)
                self.dayId = o.base.time.getDayId(self.epoch)
            gevent.sleep(0.5)

    def _minRepeat(self):
        while True:
            gevent.sleep(5)
            for key in self.schedule1min.keys():
                item, args, kwargs = self.schedule1min[key]
                item(*args, **kwargs)

    def _15minRepeat(self):
        while True:
            gevent.sleep(60*15)
            for key in self.schedule15min.keys():
                item, args, kwargs = self.schedule15min[key]
                item(*args, **kwargs)

    def _60minRepeat(self):
        while True:
            gevent.sleep(60*60)
            for key in self.schedule60min.keys():
                item, args, kwargs = self.schedule60min[key]
                item(*args, **kwargs)

    def addSchedule1MinPeriod(self, name, method, *args, **kwargs):
        self.schedule1min[name] = (method, args, kwargs)

    def addSchedule15MinPeriod(self, name, method, *args, **kwargs):
        self.schedule15min[name] = (method, args, kwargs)

    def addSchedule60MinPeriod(self, name, method, *args, **kwargs):
        self.schedule60min[name] = (method, args, kwargs)

    def start(self, routes=None, wiki=True, reset=False):
        """
        Start the web server, serving the `routes`. When no `routes` dict is passed, serve a single 'test' route.

        This method will block until an exception stops the server.

        @param routes: routes to serve, will be merged with the already added routes
        @type routes: dict(string, list(callable, dict(string, string), dict(string, string)))
        """
        if routes:
            self.routes.update(routes)

        if wiki:
            self.loadSpaces(reset=reset)

        TIMER = gevent.greenlet.Greenlet(self._timer)
        TIMER.start()

        S1 = gevent.greenlet.Greenlet(self._minRepeat)
        S1.start()

        S2 = gevent.greenlet.Greenlet(self._15minRepeat)
        S2.start()

        S3 = gevent.greenlet.Greenlet(self._60minRepeat)
        S3.start()

        o.console.echo("webserver started on port %s" % self.port)
        self.webserver.serve_forever()

    def getNow(self):
        return self.epoch

    def loadFromConfig4loader(self, loader, reset=False):
        if self.cfgdir == "":
            cfgpath = o.system.fs.joinPaths("cfg", "contentdirs.cfg")
        else:
            cfgpath = o.system.fs.joinPaths(self.cfgdir, "contentdirs.cfg")
        wikicfg = ""
        if o.system.fs.exists(cfgpath):
            wikicfg = o.system.fs.fileGetContents(cfgpath)

        paths = wikicfg.split("\n")
        self.basepath = o.system.fs.joinPaths(o.system.fs.getParent(self.cfgdir), "base")
        o.system.fs.createDir(self.basepath)
        if self.basepath not in paths:
            paths.append(self.basepath)

        appdir = o.core.portal.runningPortal.appdir
        paths.append(o.system.fs.joinPaths(appdir, "wiki"))

        for path in paths:
            path = path.strip()
            if path != "" and path[0] != "#":
                print "import from %s" % path
                if path[0].replace("\\", "/") != "/" and path.find(":") == -1:
                    path = o.system.fs.joinPaths(o.system.fs.getParent(self.cfgdir), path)
                self.contentdirs[path.replace("\\", "/").replace("/", "_").replace(":", "").rstrip("_").lower()] = path
                loader.scan(path, reset)

    def loadSpaces(self, reset=False):
        if reset:
            self.bucketsloader = o.core.portalloader.getBucketsLoader()
            self.spacesloader = o.core.portalloader.getSpacesLoader()
            o.core.codegenerator.resetMemNonSystem()
            o.core.specparser.resetMemNonSystem()
            # self.actorsloader=ActorsLoader()
            self.contentdirs = {}

        self.loadFromConfig4loader(self.bucketsloader)
        self.loadFromConfig4loader(self.spacesloader)

        if "system" not in self.spacesloader.spaces:
            raise RuntimeError("could not find system space")

        self.spacesloader.spaces["system"].loadDocProcessor()

        for actorid in o.core.portal.runningPortal.actorsloader.id2object.keys():
            actorloader = o.core.portal.runningPortal.actorsloader.id2object[actorid]
            actorloader.loadSpace()

    def getSpaces(self):
        return self.spacesloader.id2object.keys()

    def getBuckets(self):
        return self.bucketsloader.id2object.keys()

    def getActors(self):
        return o.core.portal.runningPortal.actorsloader.id2object.keys()

    def getSpace(self, name):
        name = name.lower()
        if name not in self.spacesloader.spaces:
            raise RuntimeError("Could not find space %s" % name)
        space = self.spacesloader.spaces[name]
        if space.docprocessor == None:
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

    def stop(self, *args):
        if self.webserver:
            self.webserver.stop()

    def ping(self, *args):
        return "ping"

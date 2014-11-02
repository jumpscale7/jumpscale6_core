

from JumpScale import j

import mimeparse
import mimetypes

class PortalRest():

    def __init__(self, webserver):
        self.ws=webserver


    def validate(self, auth, ctx):
        if ctx.params == "":
            msg = 'No parameters given to actormethod.'
            ctx.start_response('400 Bad Request', [])
            return False, msg
        if auth and ctx.env['beaker.session']['user'] == 'guest':
            msg = 'NO VALID AUTHORIZATION KEY GIVEN, use get param called key (check key probably auth error).'
            ctx.start_response('401 Unauthorized', [])
            return False, msg

        paramCriteria = self.ws.routes[ctx.path][1]
        paramOptional = self.ws.routes[ctx.path][3]

        for key in paramCriteria.keys():
            criteria = paramCriteria[key]
            if key not in ctx.params:
                if key in paramOptional:
                    # means is optional
                    ctx.params[key] = None
                else:
                    ctx.start_response('400 Bad Request', [])
                    message = 'get param with name:%s is missing.' % key
                    return False, message
            elif (criteria != "" and ctx.params[key] == "")\
                    or (criteria != "" and not j.codetools.regex.matchAllText(criteria, ctx.params[key])):
                ctx.start_response('400 Bad Request', [])
                msg = 'value of param %s not correct needs to comform to regex %s' % (key, criteria)
                return False, msg
        return True, ""

    def restPathProcessor(self, path):
        """
        Function which parse a path, returning True or False depending on
        successfull parsing, a error message and a dict of parameters.
        When successfull the params dict contains the path elements otherwise it
        contains if provided the actorname  and appname.
        """
        j.logger.log("Process path %s" % path, 9)
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
            params["appname"] = appname
            params["actorname"] = actor
            return (False, msginfo, params)
        params["paths"] = paths
        return (True, "", params)

    def restRouter(self, env, start_response, path, paths, ctx, ext=False, routekey=None, human=False):
        """
        does validaton & authorization
        returns right route key
        """
        if not routekey:
            routekey = "%s_%s_%s" % (paths[0], paths[1], paths[2])
        # j.logger.log("Execute %s %s" % (env["REMOTE_ADDR"], routekey))
        routes = self.ws.routes
        if routekey not in routes:
            self.activateActor(paths[0], paths[1])
        
        if routekey not in routes:
            routekey="GET_%s"%routekey

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
            resultcode, msg = self.validate(auth, ctx) #validation & authorization (but user needs to be known)
            if resultcode == False:                
                if human:
                    params = {}
                    params["error"] = "Incorrect Request: %s" % msg
                    params["appname"] = ctx.application
                    params["actorname"] = ctx.actor
                    params["method"] = ctx.method
                    page = self.ws.returnDoc(ctx, start_response, "system",
                                          "restvalidationerror", extraParams=params)
                    return (False, ctx, [str(page)])
                else:
                    return (False, ctx, msg)
            else:
                return (True, ctx, routekey)
        else:
            msg = "Could not find method, path was %s" % (path)
            appname = paths[0]
            actor = paths[1]
            contentType, data = self.ws.reformatOutput(ctx, msg, restreturn=not human)
            ctx.start_response("404 Not Found", [('Content-Type', contentType)])
            if human:
                page = self.getServicesInfo(appname, actor)
                return (False, ctx, self.ws.raiseError(ctx=ctx, msg=msg,msginfo=str(page)))
            else:
                contentType, data = self.ws.reformatOutput(ctx, msg, restreturn=False)
                return (False, ctx, data)

    def execute_rest_call(self, ctx, routekey, ext=False):
        routes = self.ws.routes
        try:
            method = routes[routekey][0]
            result = method(ctx=ctx, **ctx.params)
            return (True, result)
        except Exception as errorObject:
            eco = j.errorconditionhandler.parsePythonErrorObject(errorObject)
            msg = "Execute method %s failed." % (routekey)
            return (False, self.ws.raiseError(ctx=ctx, msg=msg, errorObject=eco))

    def processor_rest(self, env, start_response, path, human=True, ctx=False):
        """
        orignal rest processor (get statements)
        e.g. http://localhost/restmachine/system/contentmanager/notifySpaceModification?name=www_openvstorage&authkey=1234
        """
        if ctx == False:
            raise RuntimeError("ctx cannot be empty")
        try:
            j.logger.log("Routing request to %s" % path, 9)

            def respond(contentType, msg):
                # j.logger.log("Responding %s" % msg, 5)
                if contentType:
                    ctx.start_response('200 OK', [('Content-Type', contentType)])
                # print msg
                return msg

            success, msg, params = self.restPathProcessor(path)
            if not success:
                params["error"] = msg
                if human:
                    page = self.ws.returnDoc(ctx, start_response, "system", "rest",
                                          extraParams=params)
                    return [str(page)]
                else:
                    httpcode = "404 Not Found"
                    contentType, data = self.ws.reformatOutput(ctx, msg, restreturn=True)
                    ctx.start_response(httpcode, [('Content-Type', contentType)])
                    return data
            paths = params['paths']

            success, ctx, routekey = self.restRouter(env, start_response, path,
                                                   paths, ctx, human=human)
            if not success:
                #in this case routekey is really the errormsg
                return routekey


            success, result = self.execute_rest_call(ctx, routekey)
            if not success:
                return result

            if human:
                ctx.format = "json"
                params = {}
                params["result"] = result
                return [str(self.ws.returnDoc(ctx, start_response, "system", "restresult", extraParams=params))]
            else:
                contentType, result = self.ws.reformatOutput(ctx, result)
                return [respond(contentType, result)]
        except Exception as errorObject:
            eco = j.errorconditionhandler.parsePythonErrorObject(errorObject)
            if ctx == False:
                print "NO webserver context yet, serious error"
                eco.process()
                print eco
            else:
                return self.ws.raiseError(ctx, errorObject=eco)

    def processor_restext(self, env, start_response, path, human=True, ctx=False):
        
        """
        rest processer gen 2 (not used by the original get code)
        """

        if ctx == False:
            raise RuntimeError("ctx cannot be empty")
        try:
            j.logger.log("Routing request to %s" % path, 9)

            def respond(contentType, msg):
                if contentType:
                    start_response('200 OK', [('Content-Type', contentType)])
                return msg

            success, message, params = self.restPathProcessor(path)

            if not success:
                params["error"] = message
                if human:
                    page = self.ws.returnDoc(ctx, start_response, "system", "rest",
                                          extraParams=params)
                    return [str(page)]
                else:
                    return self.ws.raiseError(ctx, message)
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
                    contentType, result = self.ws.reformatOutput(ctx, result)
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
                return [str(self.ws.returnDoc(ctx, start_response, "system", "restresult", extraParams=params))]
            else:
                contentType, result = self.ws.reformatOutput(ctx, result)
                return respond(contentType, result)
        except Exception as errorObject:
            eco = j.errorconditionhandler.parsePythonErrorObject(errorObject)
            if ctx == False:
                print "NO webserver context yet, serious error"
                eco.process()
                print eco
            else:
                return self.ws.raiseError(ctx, errorObject=eco)
 
    def activateActor(self, appname, actor):
        if not "%s_%s" % (appname, actor) in self.ws.actors.keys():
            # need to activate
            try:
                result = self.ws.actorsloader.getActor(appname, actor)
            except Exception, e:
                eco = j.errorconditionhandler.parsePythonErrorObject(e)
                eco.process()
                print e
                return False
            if result == None:
                # there was no actor
                return False


    # def _getActorInfoUrl(self, appname, actor):
    #     """
    #     used for during error show links to actor in browser
    #     """
    #     if actor == "":
    #         url = "/rest/%s/" % (appname)
    #     else:
    #         url = "/rest/%s/%s/" % (appname, actor)
    #     # url="<a href=\"%s\">go here for more info about actor %s in %s</a> " % (url,actor,appname)
    #     return url                

from JumpScale import j

class ActorsInfo():

    def getActorMethodCall(self, appname, actor, method):
        """
        used for during error show links to methods in browser
        """
        url = "/rest/%s/%s/%s?" % (appname, actor, method)

        auth = j.core.portal.active.ws.routes["%s_%s_%s" % (appname, actor, method)][5]
        if auth:
            params = ["authkey"]
        else:
            params = []
        params.extend(j.core.portal.active.ws.routes["%s_%s_%s" % (appname, actor, method)][1].keys())

        for param in params:
            url += "%s=&" % param
        url += "format=text"
        if url[-1] == "&":
            url = url[:-1]
        if url[-1] == "?":
            url = url[:-1]
        # url="<a href=\"%s\">%s</a> " % (url,url)
        return url

    def getActorInfoPage(self, appname, actorname, methodname, page=None):
        """
        used for during error show info about 1 actor
        """
        if appname == "" or actorname == "" or methodname == "":
            txt = "getActorInfo need 3 params: appname, actorname, methoname, got: %s, %s,%s" % (appname, actorname, methodname)
            return txt
        if page == None:
            page = j.core.portal.active.getpage()
        page.addHeading("%s.%s.%s" % (appname, actorname, methodname), 5)

        url = getActorMethodCall(appname, actorname, methodname)

        routekey="%s_%s_%s" % (appname, actorname, methodname)
        if not j.core.portal.active.routes.has_key(routekey):
            j.core.portal.active.activateActor(appname, actorname)
        routeData = j.core.portal.active.routes[routekey]
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

    def getActorsInfoPage(appname="", actor="", page=None, extraParams={}):
        actorsloader = j.core.portal.active.actorsloader
        if appname != "" and actor != "":
            result = j.core.portal.active.activateActor(appname, actor)
            if result == False:
                # actor was not there
                page = j.core.portal.active.getpage()
                page.addHeading("Could not find actor %s %s." % (appname, actor), 4)
                return page

        if page == None:
            page = j.core.portal.active.getpage()
        if appname == "":
            page.addHeading("Applications in appserver.", 4)
            appnames = {}

            for appname, actorname in actorsloader.getAppActors():  # [item.split("_", 1) for  item in self.app_actor_dict.keys()]:
                appnames[appname] = 1
            appnames = sorted(appnames.keys())
            for appname in appnames:
                link = page.getLink("%s" % (appname), getActorInfoUrl(appname, ""))
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
                link = page.getLink("%s" % (actorname), getActorInfoUrl(appname, actorname))
                page.addBullet(link)
            return page

        keys = sorted(j.core.portal.active.routes.keys())
        page.addHeading("list", 2)
        for item in keys:
            app2, actor2, method = item.split("_")
            if app2 == appname and actor2 == actor:
                url = getActorMethodCall(appname, actor, method)
                link = page.getLink(item, url)
                page.addBullet(link)

        page.addHeading("details", 2)
        for item in keys:
            app2, actor2, method = item.split("_")
            if app2 == appname and actor2 == actor:
                page = getActorInfoPage(appname, actor, method, page=page)



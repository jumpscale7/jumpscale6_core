
def main(j, args, params, tags, tasklet):
    page = args.page

    if "actorname" in args.paramsExtra:
        actorname = args.paramsExtra["actorname"]
    else:
        actorname = ""

    if "appname" in args.paramsExtra:
        appname = args.paramsExtra["appname"]
    else:
        appname = ""

    def getActorInfo(self, appname, actorname, methodname, page=None):
        """
        used for during error show info about 1 actor
        """
        if appname == "" or actorname == "" or methodname == "":
            txt = "getActorInfo need 3 params: appname, actorname, methoname, got: %s, %s,%s" % (appname, actorname, methodname)
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

    def getActorsInfo(appname="", actor="", page=None, extraParams={})
        actorsloader = j.core.portal.runningPortal.actorsloader
        if appname != "" and actor != "":
            result = j.core.portal.runningPortal.activateActor(appname, actor)
            if result == False:
                # actor was not there
                page = self.getpage()
                page.addHeading("Could not find actor %s %s." % (appname, actor), 4)
                return page

        if page == None:
            page = self.getpage()
        if appname == "":
            page.addHeading("Applications in appserver.", 4)
            appnames = {}

            for appname, actorname in actorsloader.getAppActors():  # [item.split("_", 1) for  item in self.app_actor_dict.keys()]:
                appnames[appname] = 1
            appnames = sorted(appnames.keys())
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

        keys = sorted(self.routes.keys())
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
                page = self.getActorInfo(appname, actor, method, page=page)




    page2 = getActorsInfo(appname=appname, actor=actorname)

    page.addBootstrap()
    page.addMessage(page2.body)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

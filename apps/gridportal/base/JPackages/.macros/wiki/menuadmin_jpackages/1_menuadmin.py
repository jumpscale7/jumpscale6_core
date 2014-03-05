
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags

    params.result = ""


    # spaces = sorted(j.core.portal.active.getSpaces())
    # spacestxt=""
    # for item in spaces:
    #     if item[0] != "_" and item.strip() != "" and item.find("space_system")==-1 and item.find("test")==-1 and  item.find("gridlogs")==-1:
    #         spacestxt += "%s:/%s\n" % (item, item.lower().strip("/"))


    C = """
{{menudropdown: name:Portal
Edit:/system/edit?space=$$space&page=$$page&$$querystring
--------------
Logout:/system/login?user_logoff_=1
Access:/system/OverviewAccess?space=$$space
System:/system
--------------
Grid:/grid
JPackages:/jpackages
Tests:/tests
"""
    # C+=spacestxt
    C+='}}'

#was inside
#Reload:javascript:$.ajax({'url': '/system/ReloadSpace?name=$$space'}).done(function(){location.reload()});void(0);
#ShowLogs:/system/ShowSpaceAccessLog?space=$$space
#ResetLogs:/system/ResetAccessLog?space=$$space
#Spaces:/system/Spaces
#Pages:/system/Pages?space=$$space
#ReloadAll:javascript:(function loadAll() {$.ajax({'url': '/system/ReloadApplication'});(function checkSpaceIsUp(trials) {if (trials <= 0) return;setTimeout(function() {$.ajax({'url': '/system/'}).done(function(){location.reload();console.log('Reloaded');}).error(function(){checkSpaceIsUp(trials - 1)});}, 1000);})(10);})();void(0);

    if j.core.portal.active.isAdminFromCTX(params.requestContext):
        params.result = C

    params.result = (params.result, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

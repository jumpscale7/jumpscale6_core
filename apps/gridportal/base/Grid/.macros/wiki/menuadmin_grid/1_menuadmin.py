
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
Edit:/system/edit?space=$$space&page=$$page&$$querystr
New:/system/create?space=$$space
--------------
Logout:/system/login?user_logoff_=1
Access:/system/OverviewAccess?space=$$space
System:/system
--------------
Grid:/grid
JPackages:/jpackages
Tests:/tests
--------------
Alerts:/grid/alerts
Disks:/grid/Disks
ECOs:/grid/ECOs
JumpScripts:/grid/JumpScripts
Logs:/grid/Logs
Machines:/grid/Machines
Nodes:/grid/Nodes
Processes:/grid/Processes
Stats:/grid/stat
VDisks:/grid/vdisks
"""
    # C+=spacestxt
    C+='}}'

    if j.core.portal.active.isAdminFromCTX(params.requestContext):
        params.result = C

    params.result = (params.result, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

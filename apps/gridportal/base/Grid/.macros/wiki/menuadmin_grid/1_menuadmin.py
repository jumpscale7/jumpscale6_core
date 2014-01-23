
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
--------------
Logout:/system/login?user_logoff_=1
Access:/system/OverviewAccess?space=$$space
System:/system
--------------
agentcontroller:/agentcontroller
grid:/grid
logs_errors:/gridlogs
jpackages:/jpackages
--------------
Machines:/grid/Machines
Disks:/grid/Disks
VDisks:/grid/vdisks
Nodes:/grid/Nodes
Processes:/grid/Processes
ECOs:/grid/ECOs
Logs:/grid/Logs
Alerts:/grid/alerts
JumpScripts:/grid/JumpScripts
Stats:/grid/stat
"""
    # C+=spacestxt
    C+='}}'

    if j.core.portal.active.isAdminFromCTX(params.requestContext):
        params.result = C

    params.result = (params.result, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

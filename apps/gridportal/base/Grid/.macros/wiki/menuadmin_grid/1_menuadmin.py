
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
{{menudropdown: name:Navigation
Edit:/system/edit?space=$$space&page=$$page&$$querystr
New:/system/create?space=$$space
--------------
Logout:/system/login?user_logoff_=1
--------------
Alerts:/grid/Alerts
Audits:/grid/Audits
ECOs:/grid/ECOs
Jobs:/grid/Jobs
Job Queues:/grid/jobqueues
Jumpscripts:/grid/Jumpscripts
Logs:/grid/Logs
Nodes:/grid/Nodes
Processes:/grid/Processes
Status Check:/grid/checkstatus
"""
    # C+=spacestxt
    C+='}}'

    if j.core.portal.active.isAdminFromCTX(params.requestContext):
        params.result = C

    params.result = (params.result, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor=j.apps.actorsloader.getActor("system","logs")
    #this makes sure bootstrap datatables functionality is used
    out="{{datatables_use}}\n\n"

    out+="||App Name||Category||Start Time||Message||Level||Process ID||\n"

    nid = args.tags.getDict()["nid"] or None

    logs = actor.listLogs(nid=nid)['aaData']
    if not logs:
        params.result = ('No logs found for this node', doc)
        return params

    for log in logs:
        appname = log[0] or ''
        category = log[1] or ''
        epoch=datetime.datetime.fromtimestamp(log[2]).strftime('%Y-%m-%d %H:%M:%S') or ''
        msg = log[3] or ''
        level = log[4] or ''
        pid = log[5] or ''

        out += "|%s|%s|%s|%s|%s|%s|\n" % (appname, category, epoch, msg, pid, level)

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

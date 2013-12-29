import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")
    #this makes sure bootstrap datatables functionality is used
    out="{{datatables_use: disable_filters:True}}}}\n\n"

    fields = ['appname', 'category', 'epoch', 'message', 'level', 'pid', 'nid', 'jid']
    #[u'category', u'jid', u'level', u'parentjid', u'appname', u'pid', u'nid', u'order', u'masterjid', u'epoch', u'gid', u'private', u'aid', u'message', u'id', u'tags']

    out+="||App Name||Category||Start Time||Message||Level||Process ID||Node ID||Job ID||\n"

    nid = args.tags.getDict().get("nid", None)
    pid = args.tags.getDict().get("pid", None)

    logs = actor.getLogs(nid=nid, pid=pid)
    if not logs:
        params.result = ('No logs found', doc)
        return params

    for log in logs:
        for field in fields:
            if field == 'epoch':
                data = datetime.datetime.fromtimestamp(log[field]).strftime('%m-%d %H:%M:%S') or ''
            elif field == 'appname':
                data = '[%s|/grid/log?id=%s]' % (log['appname'], log['id'])
            elif field == 'nid':
                data = '[%s|/grid/node?id=%s]' % (log['nid'], log['nid'])
            elif field == 'pid':
                data = '[%s|/grid/process?id=%s]' % (log['pid'], log['pid'])
            else:
                data = str(log[field]).replace('[', '&#91;') #Some messages had square brackets
            out += "|%s" % data
        out += "|"
        out += "\n"

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True


def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    #['category', 'jid', 'code', 'level', 'backtrace', 'appname', 'pid', 'nid', 'funcname', 'epoch', 'errormessagePub', 'funclinenr', 'gid', 'masterjid', 'errormessage', 'type', 'funcfilename', 'tags']

    fields = ["nid", "appname", "category", "errormessagePub", "jid"]

    out.append('||nid||app name||category||error message||job ID||')

    for eco in actor.getErrorconditions():
        line = [""]

        for field in fields:
            # add links
            if field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(eco[field]), str(eco[field])))
            elif field == 'jid':
                line.append('[%s|/grid/job?id=%s]' % (str(eco[field]), str(eco[field])))
            else:
                line.append(str(eco[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

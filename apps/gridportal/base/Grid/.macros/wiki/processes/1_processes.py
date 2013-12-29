import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters:True}}\n")

    #fields = ['systempid', 'name', 'instance', 'id', 'nid', 'epochstart', 'lastcheck', 'jpdomain', 'gid', 'active', 'jpname', 'epochstop']

    fields = ["id", "nid", "name", "jpname", "jpdomain", "epochstart", "active"]

    out.append('||id||node||name||process name||process domain||start||active||')

    for process in actor.getProcesses():
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/process?id=%s]' % (str(process[field]), str(process[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(process[field]), str(process[field])))
            elif field in ('epochstart'):
                time = datetime.datetime.fromtimestamp(process[field]).strftime('%m-%d %H:%M:%S')
                line.append(str(time))
            else:
                line.append(str(process[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

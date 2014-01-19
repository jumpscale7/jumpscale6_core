import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    nid = args.tags.getDict()['nid'] if args.tags.getDict().get('nid') and not args.tags.getDict()['nid'].startswith('$$') else None

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    fields = ["systempids", "nid", "name", "jpname", "jpdomain", "epochstart", "active"]

    out.append('||pids||node||name||process name||process domain||start||active||')

    for process in actor.getProcesses(nid=nid):
        line = [""]

        for field in fields:
            # add links
            if field == 'systempids':
                pids = ', '.join([ str(x) for x in process[field]])
                line.append('[%s|/grid/process?id=%s]' % (pids, process['id']))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(process[field]), str(process[field])))
            elif field in ('epochstart'):
                time = datetime.datetime.fromtimestamp(process[field]).strftime('%m-%d %H:%M:%S')
                line.append(str(time))
            elif field == 'name':
                name = process['sname'] or process['pname']
                line.append(name)
            else:
                line.append(str(process[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

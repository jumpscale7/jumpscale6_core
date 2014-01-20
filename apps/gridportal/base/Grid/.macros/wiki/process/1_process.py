import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")
    id = args.getTag('id')
    if not id:
        out = 'Missing process id param "id"'
        params.result = (out, doc)
        return params

    obj = actor.getProcesses(id=id)
    if not obj:
        out = 'No process with id %s found' % id
        params.result = (out, doc)
        return params

    obj = obj[0]

    out = ['||Property||Value||']

    fields = ['systempids', 'name', 'instance', 'nid', 'epochstart', 'lastcheck', 'jpdomain', 'gid', 'active', 'jpname', 'epochstop']

    for field in fields:
        if field == 'nid':
            out.append("|Node|[%s|/grid/node?id=%s]|" % (obj[field], obj[field]))
        elif field in ('lastcheck', 'epochstart', 'epochstop'):
            lastchecked = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), lastchecked))
        elif field == 'systempids':
            pids = ', '.join([ str(x) for x in obj[field]])
            out.append('|Systempids|%s|' % (pids))
        elif field == 'name':
            name = obj['sname'] or obj['pname']
            out.append('|Name|%s|' % name)
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

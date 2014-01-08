import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")
    tags = args.tags.getDict()
    id = "%(gid)s_%(nid)s_%(pid)s" % (tags)


    obj = actor.getProcesses(id=id)
    if not obj:
        out = 'No process with id %s found' % id
        params.result = (out, doc)
        return params

    obj = obj[0]

    out = ['||Property||Value||']

    fields = ['systempid', 'name', 'instance', 'nid', 'epochstart', 'lastcheck', 'jpdomain', 'gid', 'active', 'jpname', 'epochstop']

    for field in fields:
        if field == 'nid':
            out.append("|Node|[%s|/grid/node?id=%s]|" % (obj[field], obj[field]))
        elif field in ('lastcheck', 'epochstart', 'epochstop'):
            lastchecked = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), lastchecked))
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

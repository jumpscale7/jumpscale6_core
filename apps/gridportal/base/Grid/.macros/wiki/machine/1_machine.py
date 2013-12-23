import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = int(args.tags.getDict()["id"])

    obj = actor.getMachines(id=id)[0]

    out = ['||Property||Value||']

    fields = ['id', 'otherid', 'name', 'description', 'roles', 'mem', 'netaddr', 'ipaddr', 'nid', 'lastcheck', 'state', 'gid', 'active', 'cpucore', 'type']
    for field in fields:
        if field == 'nid':
            out.append("|Node|[%s|/grid/node?id=%s]|" % (obj[field], obj[field]))
        elif field in ('roles', 'ipaddr'):
            out.append("|%s|%s|" % (field.capitalize(), ', '.join(obj[field])))
        elif field == 'netaddr':
            netaddr = obj[field]
            netinfo = ''
            for k, v in netaddr.iteritems():
                netinfo += 'mac address: %s, interface: %s, ip: %s<br>' % (k, v[0], v[1])
            out.append("|%s|%s|" % (field.capitalize(), netinfo))
        elif field == 'lastcheck':
            lastchecked = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), lastchecked))
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

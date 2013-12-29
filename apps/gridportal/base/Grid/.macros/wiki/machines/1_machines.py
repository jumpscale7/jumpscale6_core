
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters: True}}}}\n")

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters: True}}}}\n")

    #[u'otherid', u'description', u'roles', u'mem', u'netaddr', u'ipaddr', u'nid', u'lastcheck', u'state', u'gid', u'active', u'cpucore', u'type', u'id', u'name']
    fields = ["id", "nid", "name", "description", "active", "state", "mem", "netaddr", "cpucore"]

    out.append('||id||node||name||description||active||state||mem||macaddr||ip||cpucore||')

    for machine in actor.getMachines():
        line = [""]

        for field in fields:
        # add links
            if field == 'id':
                line.append('[%s|/grid/machine?id=%s]' % (str(machine[field]), str(machine[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(machine[field]), str(machine[field])))
            elif field == 'netaddr':
                netaddr = machine[field]
                macs = ''
                ips = ''
                for k, v in netaddr.iteritems():
                    macs += '%s<br>' % k
                    ips += '%s:%s<br>' % (v[0], v[1])
                line.append('%s|%s' % (macs, ips))
            else:
                line.append(str(machine[field]))

        line.append("")
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

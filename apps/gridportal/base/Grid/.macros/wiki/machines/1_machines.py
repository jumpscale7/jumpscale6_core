
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    #[u'otherid', u'description', u'roles', u'mem', u'netaddr', u'ipaddr', u'nid', u'lastcheck', u'state', u'gid', u'active', u'cpucore', u'type', u'id', u'name']
    fields = ["id", "nid", "name", "description", "active", "state", "mem", "netaddr", "cpucore"]

    out.append('||ID||Node||Name||Description||Active||State||Mem||Macaddr||IP||CPUCore||')
    machines = actor.getMachines()
    if not machines:
        out = 'No machines available'
        params.result = (out, doc)
        return params

    for machine in machines:
        line = [""]

        for field in fields:
        # add links
            if field == 'id':
                line.append('[%s|/grid/machine?id=%s]' % (str(machine[field]), str(machine[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(machine[field]), str(machine[field])))
            elif field == 'netaddr':
                netaddr = machine[field]
                macs = list()
                ips = list()
                for k, v in netaddr.iteritems():
                    macs.append('%s' % k)
                    iface, ip = v
                    if not ip:
                        ip = 'N/A'
                    ips.append('%s %s' % (iface, ip))
                line.append('%s|%s' % ('@LF '.join(macs), '@LF '.join(ips)))
            else:
                line.append(str(machine[field]))

        line.append("")
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

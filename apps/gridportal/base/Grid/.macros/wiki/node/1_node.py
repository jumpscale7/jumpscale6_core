
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    idd = int(args.tags.getDict()["id"])

    obj = actor.getNodes(id=idd)[0]

    out = ['||Property||Value||']

    out.append("|id|%s|" % (obj['id']))
    out.append("|node (remove this field?)|%s|" % (obj['nid']))

    n = 1
    for i in obj['netaddr']:
        out.append("|net %s mac address|%s|" % (n, i))
        out.append("|net %s port|%s|" % (n, obj['netaddr'][i][0]))
        out.append("|net %s IP address|%s|" % (n, obj['netaddr'][i][1]))
        n += 1

    # IP addresses: duplicate information, remove field?
    n = 1
    for i in obj['ipaddr']:
        out.append("|IP address %s|%s|" % (n, i))
        n +=1

    out.append("|%s|[%s|/node?id=%s]|" % ('peer log', obj['peer_log'], obj['peer_log']))
    out.append("|%s|[%s|/node?id=%s]|" % ('peer stats', obj['peer_stats'], obj['peer_stats']))
    out.append("|%s|[%s|/node?id=%s]|" % ('peer backup', obj['peer_backup'], obj['peer_backup']))
    out.append("|%s|%s|" % ('machine guid', obj['machineguid']))
    out.append("|%s|%s|" % ('active', obj['active']))
    out.append("|%s|%s|" % ('name', obj['name']))
    out.append("|%s|%s|" % ('description', obj['description']))

    params.result = ('\n'.join(out), doc)


    return params


def match(j, args, params, tags, tasklet):
    return True

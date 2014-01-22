
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    idd = args.getTag("id")
    if not idd:
        out = 'Missing node id param "id"'
        params.result = (out, doc)
        return params

    node = actor.getNodes(id=idd)
    if not node:
        params.result = ('Node with id %s not found' % idd, doc)
        return params

    obj = node[0]

    out = ['h2. Node %s' % obj['id']]

    out.append("{{nodestat: nid:%s cpustats}}" % idd)

    out.append("h3. Details")

    out.append("|%s|%s|" % ('*Name*', obj['name'] or 'None'))
    out.append("|%s|%s|" % ('*Active*', obj['active']))
    out.append("|%s|%s|" % ('*Roles*', ', '.join(obj['roles']) or 'None'))
    out.append("|%s|%s|" % ('*Description*', obj['description'] or 'None'))
    out.append("|%s|%s|" % ('*Statistics*', '[Go to statistics page|NodeStats?id=%s]' % idd))
    out.append("|%s|%s|" % ('*CPU Real Time Statistics*', '[Go to real time stats for CPU page|realtimestats?nid=%s&statistic=cpupercent]' % idd))
    out.append("|%s|%s|" % ('*Memory Real Time Statistics*', '[Go to real time stats for memory page|realtimestats?nid=%s&statistic=mempercent]' % idd))
    out.append("|%s|%s|" % ('*Network Real Time Statistics*', '[Go to real time stats for network page|realtimestats?nid=%s&statistic=netstat]' % idd))

    # Display only if peers are actually defined
    if obj['peer_log'] > 0:
        out.append("|%s|[%s|/grid/node?id=%s]|" % ('peer log', obj['peer_log'], obj['peer_log']))
    if obj['peer_stats'] > 0:
        out.append("|%s|[%s|/grid/node?id=%s]|" % ('peer stats', obj['peer_stats'], obj['peer_stats']))
    if obj['peer_backup'] > 0:
        out.append("|%s|[%s|/grid/node?id=%s]|" % ('peer backup', obj['peer_backup'], obj['peer_backup']))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

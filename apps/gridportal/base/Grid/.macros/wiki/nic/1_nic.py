import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.getTag("id")
    if not id:
        out = 'Missing nic id param "id"'
        params.result = (out, doc)
        return params

    obj = actor.getNics(id=id)[0]

    out = ['h2. NIC %s' % obj['name']]

    out.append('h3. Details')

    out.append("|*MAC Address*|%s|" % obj['mac'])
    out.append("|*IP Address*|%s|" % ', '.join(obj['ipaddr']))
    lastchecked = datetime.datetime.fromtimestamp(obj['lastcheck']).strftime('%Y-%m-%d %H:%M:%S')
    out.append("|*Last check*|%s|" % lastchecked)
    out.append("|*Node*|[%s|/grid/node?id=%s]|" % (obj['nid'], obj['nid']))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

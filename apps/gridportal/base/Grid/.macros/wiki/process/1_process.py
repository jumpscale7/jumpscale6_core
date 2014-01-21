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

    out = ["h2. Process '%s'" % obj['pname'] or 'None']

    out.append("h3. Details")

    pids = ', '.join([str(x) for x in obj['systempids']])
    out.append('|*System PIDs*|%s|' % pids)
    ports = ', '.join([str(x) for x in obj['ports']])
    out.append('|*Ports*|%s|' % ports)
    out.append("|*User*|%s|" % obj['user'])
    out.append("|*Active*|%s|" % obj['active'])
    lastchecked = datetime.datetime.fromtimestamp(obj['lastcheck']).strftime('%Y-%m-%d %H:%M:%S')
    out.append("|*Last check*|%s|" %  lastchecked)
    epochstart = datetime.datetime.fromtimestamp(obj['epochstart']).strftime('%Y-%m-%d %H:%M:%S')
    out.append("|*Started*|%s|" %  epochstart)
    epochstop = datetime.datetime.fromtimestamp(obj['epochstop']).strftime('%Y-%m-%d %H:%M:%S')
    out.append("|*Stopped*|%s|" %  epochstop)
    out.append("|*JPackage*|%s|" % obj['jpname'] or 'None')
    out.append("|*Node*|[%s|/grid/node?id=%s]|" % (obj['nid'], obj['nid']))
    out.append("|*Statistics*|[Go to statistics page|ProcessStats?id=%s]|" % id)

    params.result = ('\n'.join(out), doc)

    return params

def match(j, args, params, tags, tasklet):
    return True

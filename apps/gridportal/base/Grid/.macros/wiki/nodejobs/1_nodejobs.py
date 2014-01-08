
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor=j.apps.actorsloader.getActor("system","logs")
    nodeactor = j.apps.actorsloader.getActor("system", "gridmanager")

    #this makes sure bootstrap datatables functionality is used
    out="{{datatables_use}}\n\n"

    out+="||JSName||JSOrganization||Roles||State||\n"

    nid = args.tags.getDict()["nid"] or None
    nodes = nodeactor.getNodes(id=nid)
    if not nodes:
        params.result = ('No jobs found for this node', doc)
        return params
    
    roles = ' or '.join(nodes[0].get('roles')) or None

    jobs = actor.listJobs(roles=roles)['aaData']
    if not jobs:
        params.result = ('No jobs found for this node', doc)
        return params

    for job in jobs:
        jsname = job[0] or ''
        jsorganization = job[1] or ''
        roles=",".join(job[3].split(',')) or ''
        state = job[4] or ''
        link = job[5].rsplit('href=')[1].rsplit('>')[0] or ''

        out += "|[%s|%s]|%s|%s|%s|\n" % (jsname, link, jsorganization, roles, state)

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

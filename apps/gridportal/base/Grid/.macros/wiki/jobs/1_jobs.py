
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    nid = args.getTag("nid")
    if not nid and args.tags.tagExists('nid'):
        out = 'Missing node id param "id"'
        params.result = (out, doc)
        return params

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    #[u'lock', u'timeStop', u'lockduration', u'result', u'id', u'category', u'jsname', u'children', u'source', u'state', u'gid', u'childrenActive', u'jscriptid', u'description', u'parent', u'args', u'sessionid', u'jsorganization', u'roles', u'timeStart', u'timeout', u'resultcode']

    fields = ["id", "category", "result", "jsname", "jsorganization", "state", "description"]

    out.append('||id||category||result||jsname||jsorganization||state||description||')


    jsname = args.getTag('jsname')
    jsorganization = args.getTag('jsorganization')

    jobs = actor.getJobs(nid=nid, jsname=jsname, jsorganization=jsorganization)
    if not jobs:
        params.result = ('No jobs found', doc)
        return params
        
    for job in jobs:
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/job?id=%s]' % (str(job[field]), str(job[field])))
            else:
                line.append(str(job[field]))

        line.append("")
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

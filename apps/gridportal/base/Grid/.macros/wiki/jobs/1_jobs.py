
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    #[u'lock', u'timeStop', u'lockduration', u'result', u'id', u'category', u'jsname', u'children', u'source', u'state', u'gid', u'childrenActive', u'jscriptid', u'description', u'parent', u'args', u'sessionid', u'jsorganization', u'roles', u'timeStart', u'timeout', u'resultcode']

    fields = ["id", "category", "result", "jsname", "jsorganization", "state", "description"]

    out.append('||id||category||result||jsname||jsorganization||state||description||')


    jsname = args.tags.getDict().get('jsname', None) if args.tags.getDict().get("jsname") and not args.tags.getDict().get('jsname', None).startswith('$$') else None
    jsorganization = args.tags.getDict().get('jsorganization', None) if args.tags.getDict().get("jsorganization") and not args.tags.getDict().get('jsorganization', None).startswith('$$') else None

    jobs = actor.getJobs(jsname=jsname, jsorganization=jsorganization)
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

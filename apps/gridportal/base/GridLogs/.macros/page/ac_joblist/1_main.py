import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    qsparams = args.requestContext.params
    path = qsparams.pop('path', None)
    rights = qsparams.pop('rights', None)

    import JumpScale.grid.osis
    osiscl = j.core.osis.getClient()
    client = j.core.osis.getClientForCategory(osiscl, 'system', 'job')
    
    header = ["ID", "Roles", "Started", "Stopped",  "JSName", "JSOrg", "Timeout", "SessionID", "Status"]
    rows = list()

    if not qsparams:
        jobs = client.search("null")
    else:
        query = {'query': {'bool': {'must': list()}}}
        if 'from' in qsparams:
            starting = j.base.time.getEpochAgo(qsparams.get('from'))
            qsparams.pop('from', None)
            drange = {'range': {'timeStart': {'gte': starting}}}
            query['query']['bool']['must'].append(drange)
        if 'to' in qsparams:
            ending = j.base.time.getEpochAgo(qsparams.get('to'))
            qsparams.pop('to', None)
            if query['query']['bool']['must']:
                query['query']['bool']['must'][0]['range']['timeStart']['lte'] = ending
            else:
                drange = {'range': {'timeStart': {'lte': ending}}}
                query['query']['bool']['must'].append(drange)

        for param in qsparams:
            term = {'term': {param: qsparams[param]}}
            query['query']['bool']['must'].append(term)

        jobs = client.search(query)

    if 'result' in jobs: 
        for job in jobs['result']:
            job = job['_source']
            started = datetime.datetime.fromtimestamp(job["timeStart"]).strftime('%d/%m %H:%M')
            stopped = datetime.datetime.fromtimestamp(job["timeStop"]).strftime('%d/%m %H:%M')
            rows.append(["%s__/gridlogs/Job?jobid=%s" % (job['id'], job['id']), job['roles'], started, stopped, job["jsname"], job["jsorganization"], job["timeout"], job['sessionid'], job['state'] ])

    page.addList(rows, header, linkcolumns=[0], classparams='table-striped table-bordered') #TODO make agentid a link to agent

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

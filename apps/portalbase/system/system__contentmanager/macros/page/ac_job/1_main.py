import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.elasticsearch
    page = args.page
    p = args.requestContext.params
    jobid = p["jobid"]

    client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234",category="agent")
    
    jobs = client.listJobs()
    for job in jobs:
        if job['id'] == jobid:
            break

    bullets = []
    for k,v in job.iteritems():
        if k == 'id':
            continue
        bullets.append('%s : %s' % (k,v))

    page.addHeading("ID: %s" % jobid, 5)
    page.addBullets(bullets)

    #get jog logs from elasticsearch TODAY TODO get it from gridmaster?
    eclient = j.clients.elasticsearch.get()
    query = {'fields': ['id', 'jid', 'message'], 'query': {'match': {'jid': jobid}}}
    result = eclient.search(index='clusterlog', query=query, es_from=0, size=20)
    hits = result.get('hits', dict()).get('hits', list())
    items = list()
    for hit in hits:
        for name, value in hit['fields'].iteritems():
            items.append("%s: %s" % (name, value))
    page.addBullets(items)


    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

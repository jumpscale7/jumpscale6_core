import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):
    import json
    import JumpScale.grid.osis
    osiscl = j.core.osis.getClient()
    client = j.core.osis.getClientForCategory(osiscl, 'system', 'job')
    page = args.page
    p = args.requestContext.params
    jobid = p["jobid"]

    job = client.get(jobid)

    page.addHeading("Job ID: %s" % jobid, 5)
    query = {'query': {'bool': {'must': [{'term': {'jid': jobid}}]}}}
    page.addLink("Logs", "/system/SystemLogs?source=%s" % json.dumps(query))
    page.addHeading("Details", 5)
    rows = list()
    for k,v in sorted(job.iteritems()):
        v = v or ""
        if k in ('guid', 'id'):
            continue
        elif k in ('timeStop', 'timeStart'):
            v = datetime.datetime.fromtimestamp(v).strftime('%Y-%m-%d %H:%M:%S') if v else 'N/A'

        if k == 'args':
            rows.append(["<th>%s</th>" %k,"", ""])
            for ka, va in v.iteritems():
                rows.append(["<th></th>", ka,va])
        elif k in ('children', 'childrenActive'):
            rows.append(["<th>%s</th>" %k,"", ""])
            for kc in v:
                rows.append(["<th></th>", "",kc])
        else:
            rows.append(["<th>%s</th>" %k,"", v])


    page.addList(rows )

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

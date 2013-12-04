import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    import JumpScale.grid.osis
    osiscl = j.core.osis.getClient()
    client = j.core.osis.getClientForCategory(osiscl, 'system', 'job')
    
    header = ["ID", "Roles", "Started", "Stopped",  "JSName", "JSOrg", "Timeout", "SessionID", "Status"]
    rows = []
    jobs = client.search("null") # TODO refine this query
    if 'result' in jobs: 
        for job in jobs['result']:
            job = job['_source']
            started = datetime.datetime.fromtimestamp(job["timeStart"]).strftime('%d/%m %H:%M')
            stopped = datetime.datetime.fromtimestamp(job["timeStop"]).strftime('%d/%m %H:%M')
            rows.append(["%s__/System/Job?jobid=%s" % (job['id'], job['id']), job['roles'], started, stopped, job["jsname"], job["jsorganization"], job["timeout"], job['sessionid'], job['state'] ])

    page.addList(rows, header, linkcolumns=[0], classparams='table-striped table-bordered') #TODO make agentid a link to agent

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

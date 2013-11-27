import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    jobid = params.jobid

    client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234",category="agent")
    
    jobs = client.listJobs()
    for job in jobs:
        if job['id'] == jobid:
            break

    bullets = []
    for k,v in job.iteritems():
        bullets.append('%s : %s' % (k,v))

    page.addHeading(jobid, 5)
    page.addBullets(bullets)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

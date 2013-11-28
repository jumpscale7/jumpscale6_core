import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234",category="agent")
    
    header = ["ID", "Roles", "JSName", "JScriptID", "JSOrganization", "args", "Timeout", "SessionID", "Children", "Status"]
    rows = []
    jobs = client.listJobs()
    for job in jobs:
        status = 'Active' if job["isactive"] else 'Inactive'
    #     started = datetime.datetime.fromtimestamp(session["start"]).strftime('%Y-%m-%d %H:%M:%S')
    #     polled = datetime.datetime.fromtimestamp(session["lastpoll"]).strftime('%Y-%m-%d %H:%M:%S')
        rows.append(["%s__/Docs/ACJob?jobid=%s" % (job['id'], job['id']), job['roles'], job["jsname"], job["jscriptid"], job["jsorganization"], job["args"], job["timeout"], job['sessionid'], job['children'], status])

    page.addList(rows, header, linkcolumns=[0]) #TODO make agentid a link to agent

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

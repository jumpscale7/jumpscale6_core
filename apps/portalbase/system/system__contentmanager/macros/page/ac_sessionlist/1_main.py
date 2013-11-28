import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234",category="agent")
    
    header = ["ID", "Role", "NetInfo", "Organization", "AgentID", "User", "Started", "Last Polled", "Status"]
    rows = []
    sessions = client.listSessions()
    for session in sessions:
        status = 'Active' if session["activejob"] else 'Inactive'
        started = datetime.datetime.fromtimestamp(session["start"]).strftime('%Y-%m-%d %H:%M:%S')
        polled = datetime.datetime.fromtimestamp(session["lastpoll"]).strftime('%Y-%m-%d %H:%M:%S')
        rows.append(["%s__/Docs/ACSession?sessionid=%s" % (session['id'], session['id']), session['roles'], session["netinfo"], session["organization"], session["agentid"], session["user"], started, polled, status])

    page.addList(rows, header, linkcolumns=[0]) #TODO make agentid a link to agent

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

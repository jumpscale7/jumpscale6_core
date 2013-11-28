import JumpScale.grid.geventws
import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    p = args.requestContext.params
    sessionid = p["sessionid"]

    client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234",category="agent")
    
    sessions = client.listSessions()
    for session in sessions:
        if session['id'] == sessionid:
            break

    bullets = []
    for k,v in session.iteritems():
        if k == 'id':
            continue
        bullets.append('%s : %s' % (k,v))

    page.addHeading("ID: %s" % sessionid, 5)
    page.addBullets(bullets)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

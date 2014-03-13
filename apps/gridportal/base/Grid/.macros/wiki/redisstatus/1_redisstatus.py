import JumpScale.grid.agentcontroller
import gevent

def main(j, args, params, tags, tasklet):
    doc = args.doc

    def getClient(clienttype, nodeip):
        client = None
        with gevent.Timeout(3, False):
            client = j.clients.agentcontroller.getClientProxy(clienttype, nodeip)
        if client is None:
            errmsg = 'Could not reach AgentController. Please check your services.'
            params.result = (errmsg, doc)
            return params
        return client

    addnote = False
    out = list()

    out.append('||Node Name||Test||Status||Description||Additional Notes||')

    for node in j.apps.system.gridmanager.getNodes():
        nodeip = node['ipaddr'][0]
        nid = node['id']
        
        redisStatus = None
        redisSize = None

        agentclient = getClient('agent', nodeip)
        with gevent.Timeout(3, False):
            redisSize = agentclient.checkRedisSize(_agentid=nid)
        if redisSize == None:
            redisSize = 'N/A'
            addnote = True
        out.append('|[*%s*|node?id=%s]|Redis Size|%s|Checks if Redis db size is less than 50MB||' % (node['name'], nid, redisSize))

        with gevent.Timeout(3, False):
            redisStatus = agentclient.checkRedisStatus(_agentid=nid)
        if redisStatus == None:
            redisStatus = 'N/A'
            addnote = True
        notes = ''
        if isinstance(redisStatus, list):
            notes = 'Unreachable: %s' % ', '.join(redisStatus)
            redisStatus = False
        out.append('||Redis Status|%s|Checks status of each redis instance on node|%s|' % (redisStatus, notes))


    if addnote:
        out.append("&#42; Means data could not be retreived from ProcessManager of that node, likely it is not running.")
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



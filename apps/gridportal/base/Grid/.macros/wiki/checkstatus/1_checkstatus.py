
import JumpScale.grid.agentcontroller
import gevent

def main(j, args, params, tags, tasklet):
    doc = args.doc

    def getClient(clienttype):
        client = None
        with gevent.Timeout(3, False):
            client = j.clients.agentcontroller.getClientProxy(clienttype)
        if client is None:
            errmsg = 'Could not reach AgentController. Please check your services.'
            params.result = (errmsg, doc)
            return params
        return client

    addnote = False
    out = list()
    out = ['||Node Name||Test||Status||Description||Additional Notes||']

    for node in j.apps.system.gridmanager.getNodes():
        nid = node['id']
        
        heartbeat = None
        redisStatus = None
        redisSize = None
        esdata = None

        processclient = getClient('process')
        with gevent.Timeout(3, False):
            heartbeat = processclient.checkHeartbeat(_agentid=nid)
        if heartbeat == None:
            heartbeat = 'N/A'
            addnote = True
        out.append('|[*%s*|node?id=%s]|Process manager|%s|Processmanager has been checked in the last two minutes||' % (node['name'], node['id'], heartbeat))

        with gevent.Timeout(3, False):
            esdata = processclient.checkES(_agentid=nid)
        if esdata == None:
            esdata = 'N/A'
            addnote = True
        if esdata['size']:
            size = esdata['size']/1024
            esnotes = 'Size = %sMB' % size
        out.append('||Elasticsearch|%s|Health and size of ElasticSearch|%s|' % (esdata['health'], esnotes or ''))

        agentclient = getClient('agent')
        with gevent.Timeout(3, False):
            redisSize = agentclient.checkRedisSize(_agentid=nid)
        if redisSize == None:
            redisSize = 'N/A'
            addnote = True
        out.append('||Redis Size|%s|Checks if Redis db size is less than 50MB||' % redisSize)

        with gevent.Timeout(3, False):
            redisStatus = agentclient.checkRedisStatus(_agentid=nid)
        if redisStatus == None:
            redisStatus = 'N/A'
            addnote = True
        if isinstance(redisStatus, list):
            notes = 'Unreachable: %s' % ', '.join(redisStatus)
            redisStatus = False
        out.append('||Redis Status|%s|Checks status of each redis instance on node|%s|' % (redisStatus, '' or notes))


    if addnote:
        out.append("&#42; Means data could not be retreived from ProcessManager of that node, likely it is not running.")
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



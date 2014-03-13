import JumpScale.grid.agentcontroller
import gevent

def main(j, args, params, tags, tasklet):
    doc = args.doc

    processclient = None
    with gevent.Timeout(3, False):
        processclient = j.clients.agentcontroller.getClientProxy('process')
    if processclient is None:
        errmsg = 'Could not reach AgentController. Please check your services.'
        params.result = (errmsg, doc)
        return params

    addnote = False
    esdata = None
    heartbeat = None
    out = list()

    out.append('||Test||Status||Description||Additional Notes||')
    nid = j.application.whoAmI.nid
    with gevent.Timeout(3, False):
        heartbeat = processclient.checkHeartbeat(_agentid=nid)
    if heartbeat == None:
        heartbeat = 'N/A'
        addnote = True
    out.append('|Process manager|%s|Whether ProcessManager has been checked in the last two minutes||' % heartbeat)

    with gevent.Timeout(3, False):
        esdata = processclient.checkES()
    if esdata == None:
        esdata = 'N/A'
        addnote = True
    if esdata['size']:
        size = esdata['size']/1024
        esnotes = 'Size = %sMB' % size
    out.append('|Elasticsearch|%s|Health and size of ElasticSearch|%s|' % (esdata['health'], esnotes or ''))

    if addnote:
        out.append("&#42; Means data could not be retreived from ProcessManager of that node, likely it is not running.")
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True

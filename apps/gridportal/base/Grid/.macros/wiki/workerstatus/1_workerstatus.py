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

    for node in j.apps.system.gridmanager.getNodes():
        nodeip = node['ipaddr'][0]
        nid = node['id']
        
        workerdata = None

        workerclient = getClient('worker', nodeip)
        with gevent.Timeout(5, False):
            workerdata = workerclient.getWorkerStatus(_agentid=nid)
        if workerdata == None:
            workerdata = 'N/A'
            addnote = True
        else:            
            out.append('*[*%s*|node?id=%s]*' % (node['name'], nid))
            out.append('||Worker Name||Memory||CPU usage||')
            for worker, data in workerdata.iteritems():
                out.append('|%s|%s|%s|' % (worker, data['mem'], data['cpu']))


    if addnote:
        out.append("&#42; Means data could not be retreived from ProcessManager of that node, likely it is not running.")
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



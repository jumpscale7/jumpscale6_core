
import JumpScale.grid.agentcontroller
import gevent

def main(j, args, params, tags, tasklet):
    doc = args.doc

    wclient = None
    with gevent.Timeout(3, False):
        wclient = j.clients.agentcontroller.getClientProxy('worker')
    if wclient is None:
        errmsg = 'Could not reach AgentController. Please check your services.'
        params.result = (errmsg, doc)
        return params

    out = list()
    out = ['||Node Name||Default||HyperVisor||IO||']
    addnote = False
    for node in j.apps.system.gridmanager.getNodes():
        data = {'default': 0, 'io': 0, 'hypervisor': 0, 'nid': node['id'], 'nodename': node['name']}
        jobs = None
        with gevent.Timeout(3, False):
            jobs = wclient.getQueuedJobs(queue=None, _agentid=data['nid'])
        if jobs is None:
            addnote = True
            out.append('|[%(nodename)s|workersjobs?nid=%(nid)s]|N/A*|N/A*|N/A*|' % (data))
            continue

        for job in jobs:
            if job['queue'] in data:
                data[job['queue']] += 1
        out.append('|[%(nodename)s|workersjobs?nid=%(nid)s]|%(default)s|%(hypervisor)s|%(io)s|' % (data))

    if addnote:
        out.append("&#42; Means data could not be retreived from ProcessManager of that node, likely it is not running.")
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True




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
    out = ['||Node ID||Default||HyperVisor||IO||']
    for node in j.apps.system.gridmanager.getNodes():
        nid = node['id']
        data = {'default': 0, 'io': 0, 'hypervisor': 0, 'nid':nid}
        jobs = None
        with gevent.Timeout(3, False):
            jobs = wclient.getQueuedJobs(queue=None, _agentid=nid)
        if jobs is None:
            errmsg = 'Could not reach ProcessManager. Please check your services.'
            params.result = (errmsg, doc)
            return params

        for job in jobs:
            if job['queue'] in data:
                data[job['queue']] += 1
        out.append('|[%(nid)s|workersjobs?nid=%(nid)s]|%(default)s|%(hypervisor)s|%(io)s|' % (data))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



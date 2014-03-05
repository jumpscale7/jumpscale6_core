
import json
import JumpScale.grid.agentcontroller

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    acclient = j.clients.agentcontroller.get()

    activejobs = acclient.getActiveJobs()
    wclient = j.clients.agentcontroller.getClientProxy('worker')

    out = 'h3. AgentController Queues\n'
    acout = ['||Default||HyperVisor||IO||||']

    default = 0
    hypervisor = 0
    io = 0
    for job in activejobs:
        if job['queue'] == 'default':
            default += 1
        elif job['queue'] == 'hypervisor':
            hypervisor += 1
        elif job['queue'] == 'io':
            io += 1

    acout.append('|%s|%s|%s|[Details|/acjobs]|' % (default, hypervisor, io))
    acout = '\n'.join(acout)
    out += acout

    out += '\nh3. Worker Queues\n'
    wout = ['||Node ID||Default||HyperVisor||IO||']
    for node in j.apps.system.gridmanager.getNodes():
        nid = node['id']
        defaultq = wclient.getQueuedJobs(queue='default', _agentid=nid)
        hypervisorq = wclient.getQueuedJobs(queue='hypervisor', _agentid=nid)
        ioq = wclient.getQueuedJobs(queue='io', _agentid=nid)
        wout.append('|[%s|workersjobs?nid=%s]|%s|%s|%s|' % (nid, nid, len(defaultq), len(hypervisorq), len(ioq)))

    wout = '\n'.join(wout)

    out += wout

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



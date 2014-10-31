
import JumpScale.grid.agentcontroller

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    acclient = j.clients.agentcontroller.get()

    activejobs = acclient.getActiveJobs()

    out = ['||Default||HyperVisor||IO||Internal||Process||||']

    cnt = {'default': 0, 'io': 0, 'hypervisor': 0, 'internal':0, 'process':0}
    for job in activejobs:
        if job['queue'] in cnt:
            cnt[job['queue']] += 1
        if job['queue'] == '':
            cnt['default'] += 1

    out.append('|%(default)s|%(hypervisor)s|%(io)s|%(internal)s|%(process)s|[Details|acjobs]|' % (cnt))
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



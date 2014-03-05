def main(j, args, params, tags, tasklet):

    import JumpScale.grid.agentcontroller

    doc = args.doc
    nid = args.getTag('nid')
    out = list()
    out.append("h2. Node '%s' Queued Jobs" % nid)
    out.append("{{datatables_use}}}}\n")
    out.append('||ID||JScriptID||Category||Command||Start time||Stop time||State||Queue')

    workerscl = j.clients.agentcontroller.getClientProxy(category="worker")
    jobs = workerscl.getQueuedJobs(format='wiki', _agentid=nid)
    if jobs:
        out.append(jobs)
    else:
        out.append('No jobs to display.')

    params.result = ('\n'.join(out), doc)

    return params

def match(j, args, params, tags, tasklet):
    return True
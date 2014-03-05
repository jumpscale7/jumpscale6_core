def main(j, args, params, tags, tasklet):

    import JumpScale.grid.agentcontroller

    def _getJobLine(job):
        start=j.base.time.epoch2HRDateTime(job['timeStart'])
        if job['timeStop']==0:
            stop=""
        else:
            stop=j.base.time.epoch2HRDateTime(job['timeStop'])
        line="|%s|%s|%s|%s|%s|%s|%s|%s|"%(job['id'],job['jscriptid'],job['category'],job['cmd'],start,stop,job['state'],job['queue'])
        return line

    doc = args.doc
    out = list()
    out.append("h2. AgentController Jobs")
    out.append("{{datatables_use}}}}\n")
    out.append('||ID||JScriptID||Category||Command||Start time||Stop time||State||Queue||')
    
    acclient = j.clients.agentcontroller.get()
    jobs = acclient.getActiveJobs()
    if jobs:
        for job in jobs:
            out.append(_getJobLine(job))
    else:
        out.append('No jobs to display.')

    params.result = ('\n'.join(out), doc)

    return params

def match(j, args, params, tags, tasklet):
    return True
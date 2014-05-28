def main(j, args, params, tags, tasklet):

    import JumpScale.grid.agentcontroller

    def _getJobLine(job):
        start=j.base.time.epoch2HRDateTime(job['timeStart'])
        if job['timeStop']==0:
            stop="N/A"
        else:
            stop=j.base.time.epoch2HRDateTime(job['timeStop'])
        jobid = '[%s|/grid/job?id=%s]' % (job['id'], job['guid'])
        line="|%s|%s|%s|%s|%s|%s|%s|%s|%s|" % (jobid, job['state'], job['acqueue'], job['queue'], job['category'], job['cmd'], job['jscriptid'], start, stop)
        return line

    doc = args.doc
    out = list()
    out.append("{{datatables_use}}}}\n")
    out.append('||ID||State||ACQueue||Queue||Category||Command||JScriptID||Start time||Stop time||')
    
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

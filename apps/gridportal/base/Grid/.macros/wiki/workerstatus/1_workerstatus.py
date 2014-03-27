import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Worker||CPU Percent||Memory Used||Status||Last Active||')
    
    workers, errors = j.core.grid.healthchecker.checkWorkers(nid)

    for data in [workers, errors]:
        if len(data) > 0:
            data = data[nid]['workers']
            for worker, stat in data.iteritems():
                out.append('|%s|%s %%|%s|%s|%s|' % (worker, stat['cpu'], stat['mem'], 'RUNNING' if stat['status'] else 'HALTED', j.base.time.epoch2HRDateTime(stat['lastactive'])))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Worker||CPU Percent||Memory Used||Running||Last Active||')
    
    workers = j.core.grid.healthchecker.checkWorkers(nid)
    for worker, stat in workers.iteritems():
        out.append('|%s|%s %%|%.2f MB|%s|%s|' % (worker, stat['cpu'], stat['mem']/1024.0/1024.0, stat['status'], j.base.time.epoch2HRDateTime(stat['lastactive'])))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



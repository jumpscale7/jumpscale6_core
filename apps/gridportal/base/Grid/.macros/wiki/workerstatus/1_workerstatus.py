import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.units

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
                size, unit = stat['mem'].split(' ')
                size = j.tools.units.bytes.toSize(float(size), unit.replace('B', ''), 'M')
                if size > 100:
                    status = '{color:orange}*RUNNING**{color}' if stat['status'] else '{color:red}*HALTED*{color}'
                else:
                    status = '{color:green}*RUNNING*{color}' if stat['status'] else '{color:red}*HALTED*{color}'
                out.append('|%s|%s %%|%s|%s|%s|' % (worker, stat['cpu'], stat['mem'], status, j.base.time.epoch2HRDateTime(stat['lastactive'])))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



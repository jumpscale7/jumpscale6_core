import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.units
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')
    nidstr = str(nid)
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

    out = list()

    out.append('||Worker||CPU Percent||Memory Used||Status||Last Active||')

    workers = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    workers = ujson.loads(workers) if workers else dict()
    errors = ujson.loads(errors) if errors else dict()

    for data in [workers, errors]:
        if nidstr in data:
            if 'workers' in data.get(nidstr, dict()):
                wdata = data[nidstr].get('workers', list())
                for stat in wdata:
                    if 'mem' not in stat:
                        status = '{color:orange}UNKNOWN{color}'
                        out.append('|%s|%s %%|%s|%s|%s|' % (stat.get('name', ''), '0', '0', status, 'UKNOWN'))
                        continue
                    size, unit = stat['mem'].split(' ')
                    size = j.tools.units.bytes.toSize(float(size), unit.replace('B', ''), 'M')
                    if size > 100:
                        status = '{color:orange}*RUNNING**{color}'
                    else:
                        status = j.core.grid.healthchecker.getWikiStatus(stat['state'])
                    out.append('|%s|%s %%|%s|%s|%s|' % (stat.get('name', ''), stat.get('cpu', 0), stat.get('mem', 0), status, j.base.time.epoch2HRDateTime(stat.get('lastactive', 0))))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



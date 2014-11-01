import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.units
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')
    nidstr = str(nid)
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 9999)

    out = list()

    out.append('||Worker||Status||Last Active||')

    workers = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    workers = ujson.loads(workers) if workers else dict()
    errors = ujson.loads(errors) if errors else dict()

    for data in [workers, errors]:
        if nidstr in data:
            if 'workers' in data.get(nidstr, dict()):
                wdata = data[nidstr].get('workers', list())
                for stat in wdata:
                    status = j.core.grid.healthchecker.getWikiStatus(stat['state'])
                    out.append('|%s|%s|%s|' % (stat.get('name', ''), status, j.base.time.epoch2HRDateTime(stat.get('lastactive', 0))))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



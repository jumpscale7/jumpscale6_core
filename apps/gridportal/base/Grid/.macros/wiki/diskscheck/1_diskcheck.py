import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')
    nidstr = str(nid)
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 9999)

    out = list()

    disks = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    disks = ujson.loads(disks) if disks else dict()
    errors = ujson.loads(errors) if errors else dict()

    out.append('||Disk||Free Space||Status||')
    for type, data in (('error', errors), ('disk', disks)):
        if nidstr in data:
            if 'disks' in data.get(nidstr, dict()):
                ddata = data[nidstr].get('disks', list())
                for diskstat in ddata:
                    if type == 'error':
                        diskstat = diskstat.values()[0]
                    if 'state' not in diskstat:
                        continue
                    state = j.core.grid.healthchecker.getWikiStatus(diskstat.get('state', 'UNKNOWN'))
                    out.append('|%s|%s|%s|' % (diskstat.get('path', ''), diskstat.get('message', ''), state))
                out.append('\n')

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



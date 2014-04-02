import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')
    nidstr = str(nid)
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

    out = list()

    out.append('||Port||Status||Memory Used||')

    rstatus = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    rstatus = ujson.loads(rstatus) if rstatus else dict()
    errors = ujson.loads(errors) if errors else dict()

    for data in [rstatus, errors]:
        if nidstr in data:
            if 'redis' in data.get(nidstr, dict()):
                rnstatus = data[nidstr].get('redis', dict())
                for port, stat in rnstatus.iteritems():
                    if stat['alive'] is True:
                        state = '{color:green}*RUNNING*{color}'
                    elif stat['alive'] is False:
                        state = '{color:red}HALTED*{color}'
                    else:
                        state = '{color:orange}UNKOWN{color}'
                    out.append('|%s|%s|%s|' % (port, state, stat['memory_usage']))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True



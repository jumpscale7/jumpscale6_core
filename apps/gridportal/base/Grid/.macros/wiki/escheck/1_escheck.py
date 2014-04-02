import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc

    esdata = None
    out = list()
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    nidstr = str(j.application.whoAmI.nid)

    esdata = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    esdata = ujson.loads(esdata) if esdata else dict()
    errors = ujson.loads(errors) if errors else dict()

    if errors:
        errors = errors.values()
        for error in errors:
            if error.get('elasticsearch', dict()).get('state', '') == 'TIMEOUT':
                out.append('{color:red}*ElasticSearch unreachable, likely ProcessManager on Master Node is not running.*{color}')
                out = '\n'.join(out)
                params.result = (out, doc)
                return params

    for message, data in {'OK': esdata, 'HALTED': errors}.iteritems():
        if nidstr in data:
            if 'elasticsearch' in data.get(nidstr, dict()):
                data = data[nidstr].get('elasticsearch', dict())
                out.append('|Status|{color:%s}*%s*{color}|' % ('green' if message=='OK' else 'red', message))
                out.append('|%s|%s|' % ('Size', data.get('size', 'N/A')))
                out.append('|%s|%s|' % ('Memory Usage', data.get('memory_usage', 'N/A')))

                for k, v in data.get('health', dict()).iteritems():
                    if k == 'status':
                        out.append('|%s|{color:%s}*%s*{color}|' % (k.title(), v, v.upper()))
                        continue
                    k = k.replace('_', ' ')
                    out.append('|%s|%s|' % (k.title(), v))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True

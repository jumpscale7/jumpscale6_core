import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

    out.append('||Node ID||Node Name||Process Manager Status||Details||')
    data = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    data = ujson.loads(data) if data else dict()
    errors = ujson.loads(errors) if errors else dict()

    if len(data) > 0:
        for nid, checks in data.iteritems():
            if nid in errors:
                categories = errors.get(nid, dict()).keys()
                runningstring = '{color:orange}*RUNNING** (issues in %s){color}' % ', '.join(categories)
            else:
                runningstring = '{color:green}*RUNNING*{color}'
            status = checks.get('processmanager', [{'state': 'UNKOWN'}])[0]
            link = '[Details|nodestatus?nid=%s]' % nid if status['state'] == 'RUNNING' else ''
            out.append('|[%s|node?id=%s]|%s|%s|%s|' % (nid, nid, j.core.grid.healthchecker._nodenames.get(int(nid), 'UNKNOWN'), runningstring, link))

    if len(errors) > 0:
        for nid, checks in errors.iteritems():
            status = checks.get('processmanager', dict())
            if status and status['state'] != 'RUNNING':
                out.append("|[%s|node?id=%s]|%s|{color:red}*HALTED*{color}| |" % (nid, nid, j.core.grid.healthchecker._nodenames.get(int(nid), 'UNKNOWN')))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True

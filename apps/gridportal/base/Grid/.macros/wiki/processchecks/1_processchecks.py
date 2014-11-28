import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 9999)

    out.append('||Grid ID||Node ID||Node Name||Process Manager Status||Details||')
    data = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    data = ujson.loads(data) if data else dict()
    errors = ujson.loads(errors) if errors else dict()

    if len(data) > 0:
        for nid, checks in data.iteritems():
            if nid in errors:
                categories = errors.get(nid, {}).keys()
                runningstring = '{color:orange}*RUNNING** (issues in %s){color}' % ', '.join(categories)
            else:
                runningstring = '{color:green}*RUNNING*{color}'
            status = checks.get('processmanager', [{'state': 'UNKOWN'}])[0]
            gid = j.core.grid.healthchecker.getGID(nid)
            link = '[Details|nodestatus?nid=%s&gid=%s]' % (nid, gid) if status['state'] == 'RUNNING' else ''
            out.append('|%s|[%s|node?id=%s&gid=%s]|%s|%s|%s|' % (gid, nid, nid, gid, j.core.grid.healthchecker.getName(nid), runningstring, link))

    if len(errors) > 0:
        for nid, checks in errors.iteritems():
            if nid in data:
                continue
            status = checks.get('processmanager', [{'state': 'UNKOWN'}])[0]
            if status and status['state'] != 'RUNNING':
                gid = j.core.grid.healthchecker.getGID(nid)
                out.append("|%s|[%s|node?id=%s&gid=%s]|%s|{color:red}*HALTED*{color}| |" % (gid, nid, nid, gid, j.core.grid.healthchecker.getName(nid)))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True

import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson
import datetime
import time

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    out = list()
    rediscl = j.clients.redis.getByInstanceName('system', gevent=True)

    out.append('||Node ID||Node Name||Process Manager Status||Details||')
    data = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    data = ujson.loads(data) if data else dict()
    errors = ujson.loads(errors) if errors else dict()

    if errors:
        nodeids = errors.keys()
        nodenames = [j.core.grid.healthchecker.getName(nodeid) for nodeid in nodeids]
        out.append('h5. {color:red}Something on node(s) %s is not running.{color}' % ', '.join(nodenames))
        out.append('For more details, check [here|/grid/checkstatus]')
    else:
        out.append('h5. {color:green}Everything seems to be OK{color}')

    if rediscl.hexists('healthcheck:monitoring', 'lastcheck'):
        lastchecked = j.basetype.float.fromString(rediscl.hget('healthcheck:monitoring', 'lastcheck'))
        lastchecked = '{{span: class=jstimestamp|data-js=%s}}{{span}}' % lastchecked
    else:
        lastchecked = 'N/A'
    out.append('Grid was last checked at: %s.' % lastchecked)

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True

import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()
    rediscl = j.clients.redis.getByInstanceName('system', gevent=True)


    if rediscl.hexists('healthcheck:monitoring', 'lastcheck'):
        lastchecked = j.basetype.float.fromString(rediscl.hget('healthcheck:monitoring', 'lastcheck'))
        lastchecked = '{{span: class=jstimestamp|data-ts=%s}}{{span}}' % lastchecked
    else:
        lastchecked = 'N/A'
    out.append('Grid was last checked at: %s.' % lastchecked)

    out.append('||Grid ID||Node ID||Node Name||JSAgent Status||Details||')
    data = rediscl.hget('healthcheck:monitoring', 'results')
    errors = rediscl.hget('healthcheck:monitoring', 'errors')
    data = ujson.loads(data) if data else dict()
    errors = ujson.loads(errors) if errors else dict()
    rows = list()

    if len(data) > 0:
        for nid, checks in data.iteritems():
            level = 0
            if nid in errors:
                level = -1
                categories = errors.get(nid, {}).keys()
                runningstring = '{color:orange}*DEGRADED** (issues in %s){color}' % ', '.join(categories)
            else:
                level = 0
                runningstring = '{color:green}*RUNNING*{color}'
            status = checks.get('processmanager', [{'state': 'UNKOWN'}])[0]
            gid = j.core.grid.healthchecker.getGID(nid)
            link = '[Details|nodestatus?nid=%s&gid=%s]' % (nid, gid) 
            row = {'level': level, 'gid': gid, 'nid': nid}
            row['message'] = '|%s|[%s|node?id=%s&gid=%s]|%s|%s|%s|' % (gid, nid, nid, gid, j.core.grid.healthchecker.getName(nid), runningstring, link)
            rows.append(row)

    if len(errors) > 0:
        for nid, checks in errors.iteritems():
            if nid in data:
                continue
            status = checks.get('processmanager', [{'state': 'UNKOWN'}])[0]
            if status and status['state'] != 'RUNNING':
                level = -2
                gid = j.core.grid.healthchecker.getGID(nid)
                row = {'level': level, 'gid': gid, 'nid': nid}
                link = '[Details|nodestatus?nid=%s&gid=%s]' % (nid, gid)
                row['message'] = "|%s|[%s|node?id=%s&gid=%s]|%s|{color:red}*HALTED*{color}|%s|" % (gid, nid, nid, gid, j.core.grid.healthchecker.getName(nid), link)
                rows.append(row)

    def sorter(row1, row2):
        for sortkey in ('level', 'gid', 'nid'):
            if row1[sortkey] != row2[sortkey] or sortkey == 'nid':
                return cmp(row1[sortkey], row2[sortkey] )

    out.extend([x['message'] for x in sorted(rows, cmp=sorter)])
    params.result = ('\n'.join(out), doc)
    return params

def match(j, args, params, tags, tasklet):
    return True

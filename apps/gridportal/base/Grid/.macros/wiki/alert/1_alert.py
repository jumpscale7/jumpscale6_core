import JumpScale.baselib.webdis
import json

def main(j, args, params, tags, tasklet):

    key = args.getTag('key')
    gguid = args.getTag('gguid')

    for name, param in {'key':key, 'gguid':gguid}.iteritems():
        if not param:
            out = 'Missing alert param "%s"' % name
            params.result = (out, args.doc)
            return params

    webdisaddr = j.application.config.get('grid.watchdog.addr')
    webdiscl = j.clients.webdis.get(webdisaddr, 7779)
    alert = webdiscl.hget('alerts:%s' % gguid, key)

    if not alert:
        params.result = ('Alert with gguid %s and key %s not found' % (gguid, key), args.doc)
        return params

    out = list()

    links = {'gid': 'grid', 'nid': 'node', 'ecoguid': 'eco'}
    properties = [('state', 'State'), ('category', 'Category'), ('value', 'Value'),
                  ('epoch', 'Initilization Time'), ('escalationepoch', 'Escalation Time'), 
                  ('escalationstate', 'Escalation State'), ('ecoguid', 'ECO ID'), ('log', 'Log'), 
                  ('gid', 'Grid ID'), ('nid', 'Node ID'), ('message_id', 'Message ID')]

    alert = json.loads(alert)
    for field in properties:
        v = alert[field[0]]
        if isinstance(v, list):
            v = ' ,'.join(v)
        elif field[0] in ['epoch', 'escalationepoch']:
            v = j.base.time.epoch2HRDateTime(v)
        elif field[0] in ['gid', 'nid', 'ecoguid']:
            v = '[%s|%s?id=%s]' % (v, links[field[0]], v)
        elif field[0] in ['state']:
            color = 'green' if v == 'OK' else ('red' if v == 'ERROR' else 'orange')
            v = '{color:%s}%s{color}' % (color, v)
        out.append("|*%s*|%s|" % (field[1], v))

    out = '\n'.join(out)

    params.result = (out, args.doc)
    return params
    

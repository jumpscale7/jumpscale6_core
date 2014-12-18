import datetime
try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):    
    import urllib

    id = args.getTag('id')
    if not id:
        out = 'Missing job id param "id"'
        params.result = (out, args.doc)
        return params

    job = j.apps.system.gridmanager.getJobs(guid=id)
    if not job:
        params.result = ('Job with id %s not found' % id, args.doc)
        return params

    obj = job[0]

    obj['nid'] = obj.get('nid', 0)
    obj['roles'] = ', '.join(obj['roles'])
    obj['args'] = urllib.quote(obj['args'])

    if obj["state"] == "ERROR":
        obj['state'] = "FAILED"
        try:
            eco = json.loads(obj['result'])
            if j.core.portal.active.osis.exists('system', 'eco', eco['guid']):
                obj['resultline'] = '{{errorresult ecoguid:%s}}' % eco['guid']
            else:
                obj['resultline'] = "ECO: Is not available anymore"
            obj['backtrace'] = eco['backtrace']
        except Exception:
            eco = {'errormessage': obj['result']}
        obj['result'] = eco['errormessage'].replace('\n', '$LF')
    else:
        try:
            result = json.loads(obj['result'])
        except:
            result = obj['result']
        obj['result'] = j.html.escape(str(result))
        obj['resultline'] = '{{successfulresult result:%s}}' % urllib.quote(obj['result'])

    if '/' in obj['cmd']:
        obj['organization'], obj['cmd'] = obj['cmd'].split('/')
    else:
        obj['organization'] = obj['category']
   

    args.doc.applyTemplate(obj)

    params.result = (args.doc, args.doc)
    return params


def match(j, args, params, tags, tasklet):
    return True

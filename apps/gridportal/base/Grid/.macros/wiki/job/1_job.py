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

    def objFetchManipulate(id):
        obj = job[0]
        for attr in ['timeStop', 'timeStart']:
            if obj[attr] != 0:
                obj[attr] = datetime.datetime.fromtimestamp(obj[attr]).strftime('%Y-%m-%d %H:%M:%S')
            else:
                obj[attr] = 'N/A'

        obj['nid'] = obj.get('nid', 0)
        obj['roles'] = ', '.join(obj['roles'])
        obj['args'] = urllib.quote(json.dumps(obj['args']))

        if obj["state"] == "ERROR":
            obj['state'] = "FAILED"
            eco = json.loads(obj['result'])
            obj['includemacro'] = 'errorresult ecoguid:%s' % eco['guid']
            obj['result'] = eco['errormessage'].replace('\n', '$LF')
        else:
            try:
                result = json.loads(obj['result'])
            except:
                result = obj['result']
            obj['result'] = j.html.escape(str(result))

        if not obj.get('includemacro', None):
            obj['includemacro'] = 'successfulresult result:%s' % urllib.quote(obj['result'])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True

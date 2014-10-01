import datetime
import JumpScale.grid.osis

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing ECO id param "id"'
        params.result = (out, args.doc)
        return params

    oscl = j.core.osis.getClient(user='root')
    ecocl = j.core.osis.getClientForCategory(oscl, 'system', 'eco')
    try:
        obj = ecocl.get(id).__dict__
    except:
        out = 'Could not find Error Condition Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    def objFetchManipulate(id):
        obj['epoch'] = datetime.datetime.fromtimestamp(obj['epoch']).strftime('%Y-%m-%d %H:%M:%S')
        for attr in ['errormessage', 'errormessagePub']:
            obj[attr] = obj[attr].replace('\n', '<br>')
        for attr in ['jid', 'masterjid']:
            obj['jid'] = '[%(jid)s|job?id=%(jid)s]|' % obj if obj[attr] != 0 else 'N/A'
        obj['pid'] = '[%(pid)s|process?id=%(pid)s]|' % obj if obj['pid'] != 0 else 'N/A'
        obj['id'] = id
        return obj

    push2doc = j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

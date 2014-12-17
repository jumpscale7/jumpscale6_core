import datetime
import JumpScale.grid.osis

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing ECO id param "id"'
        params.result = (out, args.doc)
        return params

    oscl = j.core.osis.getClientByInstance('main')
    ecocl = j.core.osis.getClientForCategory(oscl, 'system', 'eco')
    try:
        obj = ecocl.get(id).__dict__
    except:
        out = 'Could not find Error Condition Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    obj['epoch'] = "{{div: class=jstimestamp|data-ts=%s}}{{div}}" % obj['epoch']
    obj['lasttime'] = "{{div: class=jstimestamp data-ts=%s}}{{div}}" % obj['lasttime']
    for attr in ['errormessage', 'errormessagePub']:
        obj[attr] = obj[attr].replace('\n', '<br>')
    for attr in ['jid']:
        obj['jid'] = '[%(jid)s|job?id=%(jid)s]|' % obj if obj[attr] != 0 else 'N/A'
    obj['id'] = id

    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params

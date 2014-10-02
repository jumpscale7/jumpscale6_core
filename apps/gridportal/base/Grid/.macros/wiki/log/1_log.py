import datetime

def main(j, args, params, tags, tasklet):
    guid = args.getTag('id')
    if not guid:
        out = 'Missing log guid param "id"'
        params.result = (out, args.doc)
        return params

    logs = j.apps.system.gridmanager.getLogs(guid=guid)
    if not logs:
        params.result = ('Log with guid %s not found' % guid, args.doc)
        return params

    def objFetchManipulate(id):
        obj = logs[0]
        for attr in ['epoch']:
            obj[attr] = datetime.datetime.fromtimestamp(obj[attr]).strftime('%Y-%m-%d %H:%M:%S')
        for attr in ['jid', 'masterjid', 'parentjid']:
            obj['jid'] = '[%(jid)s|job?id=%(jid)s]|' % obj if obj[attr] else 'N/A'
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


def match(j, args, params, tags, tasklet):
    return True

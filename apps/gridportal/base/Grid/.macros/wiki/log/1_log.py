import datetime

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing log id param "id"'
        params.result = (out, args.doc)
        return params

    logs = j.apps.system.gridmanager.getLogs(id=id)
    if not logs:
        params.result = ('Log with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = logs[0]
        for attr in ['epoch']:
            obj[attr] = datetime.datetime.fromtimestamp(obj[attr]).strftime('%Y-%m-%d %H:%M:%S')
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


def match(j, args, params, tags, tasklet):
    return True

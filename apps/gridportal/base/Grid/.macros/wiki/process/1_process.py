import datetime

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing process id param "id"'
        params.result = (out, args.doc)
        return params

    process = j.apps.system.gridmanager.getProcesses(id=id)
    if not process:
        params.result = ('Process with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = process[0]
        for attr in ['lastcheck', 'epochstop', 'epochstart']:
            obj[attr] = datetime.datetime.fromtimestamp(obj[attr]).strftime('%Y-%m-%d %H:%M:%S')
        obj['jpname'] = obj['jpname'] or 'None'
        obj['ports'] = ', '.join([str(x) for x in obj['ports']])
        obj['systempids'] = ', '.join([str(x) for x in obj['systempids']])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


def match(j, args, params, tags, tasklet):
    return True

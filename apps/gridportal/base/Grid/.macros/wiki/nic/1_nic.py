import datetime

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing NIC id param "id"'
        params.result = (out, args.doc)
        return params

    nics = j.apps.system.gridmanager.getNics(id=id)
    if not nics:
        params.result = ('NIC with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = nics[0]
        obj['lastcheck'] = datetime.datetime.fromtimestamp(obj['lastcheck']).strftime('%Y-%m-%d %H:%M:%S')
        obj['ipaddr'] = ', '.join([str(x) for x in obj['ipaddr']])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True

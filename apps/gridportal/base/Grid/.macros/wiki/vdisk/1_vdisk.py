import datetime

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing vdisk id param "id"'
        params.result = (out, args.doc)
        return params

    vdisks = j.apps.system.gridmanager.getVDisks(id=id)
    if not vdisks:
        params.result = ('VDisk with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = vdisks[0]
        for attr in ['lastcheck', 'expiration', 'backuptime']:
            value = obj.get(attr)
            if value: 
                obj[attr] = datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
            else:
                obj[attr] = 'N/A'
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True

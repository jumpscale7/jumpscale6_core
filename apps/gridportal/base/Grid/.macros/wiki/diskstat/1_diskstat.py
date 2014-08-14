
def main(j, args, params, tags, tasklet):
    params.merge(args)
    id = args.getTag('id')
    
    if not id:
        return params

    disks = j.apps.system.gridmanager.getDisks(id=id)
    if not disks:
        return params

    def objFetchManipulate(id):
        obj = disks[0]
        name = obj['path'].replace('/dev/', '')
        diskkey = 'n%s.disk.%s' % (obj['nid'], name)
        obj['diskkey'] = diskkey
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)
def match(j, args, params, tags, tasklet):
    return True

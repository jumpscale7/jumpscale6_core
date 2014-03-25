    
def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units

    id = args.getTag('id')
    if not id:
        out = 'Missing disk id param "id"'
        params.result = (out, args.doc)
        return params

    disks = j.apps.system.gridmanager.getDisks(id=id)
    if not disks:
        params.result = ('Disk with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = disks[0]
        obj['usage'] = 100 - int(100.0 * float(obj['free']) / float(obj['size']))
        obj['dpath'] = obj['path'] # path is reserved variable for path of request
        for attr in ['size', 'free']:
            obj[attr] = "%.2f %siB" % j.tools.units.bytes.converToBestUnit(obj[attr], 'K')
        obj['type'] = ', '.join([str(x) for x in obj['type']])
        # obj['systempids'] = ', '.join([str(x) for x in obj['systempids']])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True

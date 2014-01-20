
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc

    id = args.getTag('id')
    actor=j.apps.system.gridmanager
    width = args.getTag('width', 800)
    height = args.getTag('height', 400)


    _data = {'height':height, 'width':width}
    
    if not id:
        out = 'Missing disk id param "id"'
        params.result = (out, doc)
        return params

    obj = actor.getDisks(id=id)
    if not obj:
        out = 'No disk with id %s found' % id
        params.result = (out, doc)
        return params
    obj = obj[0]
    name = obj['path'].replace('/dev/', '')
    diskkey = 'n%s.disk.%s' % (obj['nid'], name)
    _data['diskkey'] = diskkey
    out = ''
    out += '\nh3. Disk Statistics\n'
    out += '|| || ||\n'
    out += '|{{stat key:%(diskkey)s.space_free_mb,%(diskkey)s.space_used_mb&title=Used%%20Space&graphType=pie width:%(width)s height:%(height)s}}|{{stat key:%(diskkey)s.kbytes_read,%(diskkey)s.kbytes_write&title=IO width:%(width)s height:%(height)s}}|\n' % _data

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

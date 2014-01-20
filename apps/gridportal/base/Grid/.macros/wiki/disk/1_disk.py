
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.getTag("id")
    if not id:
        out = 'Missing disk id param "id"'
        params.result = (out, doc)
        return params


    obj = actor.getDisks(id=id)[0]

    out = ['||Property||Value||']

    sizes = ['KiB', 'MiB', 'GiB', 'TiB', 'ZiB']
    def getSize(size):
        cnt = 0
        while size > 1200 or len(sizes) < cnt:
            size /= 1024.
            cnt  += 1
        return "%.2f %s" % (size, sizes[cnt])


    out.append("|%s|%s|" % ('id', obj['id']))
    out.append("|%s|[%s|/grid/node?id=%s]|" % ('node', obj['nid'], obj['nid']))
    out.append("|%s|%s|" % ('active', obj['active']))
    out.append("|%s|%s|" % ('ssd', obj['ssd']))
    out.append("|%s|%s|" % ('model', obj['model']))
    out.append("|%s|%s|" % ('path', obj['path']))
    out.append("|%s|%s|" % ('size', getSize(obj['size'])))
    out.append("|%s|%s|" % ('free', getSize(obj['free'])))
    out.append("|%s|%s%%|" % ('usage', 100 - int(100.0 * obj['free'] / obj['size'])))
    out.append("|%s|%s|" % ('filesystem', obj['fs']))
    out.append("|%s|%s|" % ('mounted', obj['mounted']))
    out.append("|%s|%s|" % ('description', obj['description']))
    out.append("|%s|%s|" % ('type', ', '.join(obj['type'])))
    out.append("|%s|%s|" % ('mountpoint', obj['mountpoint']))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

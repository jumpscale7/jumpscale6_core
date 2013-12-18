
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = int(args.tags.getDict()["id"])

    obj = actor.getDisks(id=id)[0]

    out = ['||Property||Value||']

    # fields = ["id", "nid", "active", "ssd", "model", "path", "size", "free",
    #           "fs", "mounted", "name", "description", "type", "mountpoint"]

    out.append("|%s|%s|" % ('id', obj['id']))
    out.append("|[%s|/grid/node?id=%s]|%s|" % ('node', obj['nid'], obj['nid']))
    out.append("|%s|%s|" % ('active', obj['active']))
    out.append("|%s|%s|" % ('ssd', obj['ssd']))
    out.append("|%s|%s|" % ('model', obj['model']))
    out.append("|%s|%s|" % ('path', obj['path']))
    out.append("|%s|%s|" % ('size', obj['size']))
    out.append("|%s|%s|" % ('free', obj['free']))
    out.append("|%s|%s%%|" % ('usage', 100 - int(100.0 * obj['free'] / obj['size'])))
    out.append("|%s|%s|" % ('filesystem', obj['fs']))
    out.append("|%s|%s|" % ('mounted', obj['mounted']))
    out.append("|%s|%s|" % ('name', obj['name']))
    out.append("|%s|%s|" % ('description', obj['description']))
    out.append("|%s|%s|" % ('type', obj['type']))
    out.append("|%s|%s|" % ('mountpoint', obj['mountpoint']))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True


def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    jsorganization = args.tags.getDict()["jsorganization"]
    jsname = args.tags.getDict()["jsname"]

    obj = actor.getJumpscript(jsorganization=jsorganization, jsname=jsname)

    out = ['||Property||Value||']

    for k,v in obj.iteritems():
        if k in ('args', 'roles'):
            v = ' ,'.join(v)
        if k == 'source':
            continue
        out.append("|%s|%s|" % (k.capitalize(), v.replace('\n', '') if v else v))

    out.append('\n{{code:%s}}' % obj['source'])
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

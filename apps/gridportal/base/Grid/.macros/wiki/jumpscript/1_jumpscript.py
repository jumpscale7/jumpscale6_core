
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    jsorganization = args.getTag("jsorganization")
    jsname = args.getTag("jsname")

    out = ''
    missing = False
    for k,v in {'jsorganization':jsorganization, 'jsname':jsname}.iteritems():
        if not v:
            out += 'Missing param %s.\n' % k
            missing = True

    if not missing:
        obj = actor.getJumpscript(jsorganization=jsorganization, jsname=jsname)

        out = ['||Property||Value||']

        for k,v in obj.iteritems():
            if k in ('args', 'roles'):
                v = ' ,'.join(v)
            if k == 'source':
                continue
            out.append("|%s|%s|" % (k.capitalize(), v.replace('\n', '') if v else v))

        out.append('\n{{code:\n%s\n}}' % obj['source'])
        out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True

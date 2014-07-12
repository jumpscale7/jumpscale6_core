
def main(j, args, params, tags, tasklet):

    doc = args.doc

    params.result = ""

    C = "{{menudropdown: %s\n" % args.tags
    for space in sorted(j.core.portal.active.getSpaces()):
        C += "%s:/%s\n" % (space.capitalize(), space)
    C += "}}\n"

    if j.core.portal.active.isAdminFromCTX(args.requestContext):
        params.result = C

    params.result = (params.result, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

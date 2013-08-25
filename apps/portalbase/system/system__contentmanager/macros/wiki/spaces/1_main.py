
def main(o, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc

    out = ""

    bullets = params.tags.labelExists("bullets")
    table = params.tags.labelExists("table")
    spaces = sorted(j.core.portal.runningPortal.webserver.getSpaces())

    if table:
        for item in spaces:
            out += "|[%s|/%s]|\n" % (item, item.lower().strip("/"))

    else:

        for item in spaces:
            if item[0] != "_" and item.strip() != "":
                if bullets:
                    out += "* [%s|/%s]\n" % (item, item.lower().strip("/"))
                else:
                    out += "[%s|/%s]\n" % (item, item.lower().strip("/"))

    params.result = (out, doc)

    return params


def match(o, args, params, tags, tasklet):
    return True

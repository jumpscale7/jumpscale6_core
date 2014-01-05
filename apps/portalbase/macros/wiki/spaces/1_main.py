
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc

    out = ""

    bullets = params.tags.labelExists("bullets")
    table = params.tags.labelExists("table")
    spaces = sorted(j.core.portal.active.getSpaces())

    if table:
        for item in spaces:
            out += "|[%s|/%s]|\n" % (item, item.lower().strip("/"))

    else:

        for item in spaces:
            if item[0] != "_" and item.strip() != "" and item.find("space_system")==-1:
                if bullets:
                    out += "* [%s|/%s]\n" % (item, item.lower().strip("/"))
                else:
                    out += "[%s|/%s]\n" % (item, item.lower().strip("/"))

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

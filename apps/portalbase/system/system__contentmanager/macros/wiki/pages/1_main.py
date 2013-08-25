
def main(o, arg, params,  tags, tasklet):
    params.merge(arg)
    doc = params.doc
    space = params.paramsExtra['space']
    out = ""

    spaces = j.core.portal.runningPortal.webserver.getSpaces()
    if space in spaces:
        sp = j.core.portal.runningPortal.webserver.getSpace(space)
    else:
        params.result = out, doc
        return params

    docs = sp.docprocessor.docs
    for item in sorted(docs, key=lambda x: x.pagename):
        spacename = item.getSpaceName()
        pagename = item.pagename
        out += "|[%s|/%s/%s] | [Edit | /system/edit?space=%s&page=%s]|\n" % (pagename, spacename, pagename, spacename, pagename)

    params.result = (out, doc)

    return params


def match(o, args, params, tags, tasklet):
    return True

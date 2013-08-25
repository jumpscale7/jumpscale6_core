
def main(j, args, params, tags, tasklet):

    page = args.page

    page.addBootstrap()

    args = args.tags.getValues(app="", actor="", path="", bucket="", space="", page="", edit=False)

    if args["page"] == "" and args["path"] == "":
        page.addMessage("ERROR: path needs to be defined in: %s" % params.cmdstr)
        return params

    if args["app"] != "" and args["actor"] != "":
        # look for path for bucket
        aloader = j.core.portal.runningPortal.actorsloader.getActorLoaderFromId("%s__%s" % (args["app"].lower(), args["actor"].lower()))
        path = j.system.fs.joinPaths(aloader.model.path, args["path"])
    elif args["space"] != "":
        # look for path for bucket
        space = j.core.portal.runningPortal.webserver.getSpace(args["space"])
        if args["page"] != "":
            space = j.core.portal.runningPortal.webserver.getSpace(args["space"])
            doc = space.docprocessor.docGet(args["page"])
            path = doc.path
            args["edit"] = True
        else:
            path = j.system.fs.joinPaths(space.model.path, args["path"])
    elif args["bucket"] != "":
        # look for path for bucket
        bucket = j.core.portal.runningPortal.webserver.getBucket(args["bucket"])
        path = j.system.fs.joinPaths(bucket.model.path, args["path"])
    else:
        page.addMessage("ERROR: could not find file as defined in: %s" % params.cmdstr)
        return params

    content = j.system.fs.fileGetContents(path)

    page.addCodeBlock(content, path=path, exitpage=False, edit=args["edit"], spacename=args["space"], pagename=args['page'])

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

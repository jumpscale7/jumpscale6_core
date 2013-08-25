
def main(o, args, params, actor, tags, tasklet):

    params.merge(args)

    params.path = params.path.replace("\\", "/")

    if params.spacepath == None:
        space = j.core.portal.runningPortal.webserver.spacesloader.getSpaceFromId(params.spacename.lower())
        params.spacepath = space.model.path

    params.spacepath = params.spacepath.replace("\\", "/")

    params.dirname = j.system.fs.getDirName(params.path + "/", lastOnly=True)
    return params


def match(o, args, params, actor, tags, tasklet):
    return True

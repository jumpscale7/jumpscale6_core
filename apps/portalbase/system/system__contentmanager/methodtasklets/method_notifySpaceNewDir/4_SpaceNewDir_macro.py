
def main(j, args, params, actor, tags, tasklet):
    # create 3 types of macro dirs inside
    j.system.fs.createDir(j.system.fs.joinPaths(params.path, "wiki"))
    j.system.fs.createDir(j.system.fs.joinPaths(params.path, "preprocess"))
    j.system.fs.createDir(j.system.fs.joinPaths(params.path, "page"))
    params.stop = True
    return params


def match(j, args, params, actor, tags, tasklet):
    return params.dirname == ".macros"

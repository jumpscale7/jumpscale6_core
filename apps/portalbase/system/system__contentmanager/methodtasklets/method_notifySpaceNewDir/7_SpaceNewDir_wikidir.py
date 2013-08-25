
def main(j, args, params, actor, tags, tasklet):
    params.result = None

    path3 = j.system.fs.joinPaths(params.path, params.dirname + ".wiki")
    if not j.system.fs.exists(path3):
        source = j.system.fs.joinPaths(params.spacepath, ".space", "template.wiki")
        j.system.fs.copyFile(source, path3)

    params.stop = True

    return params


def match(j, args, params, actor, tags, tasklet):
    return True

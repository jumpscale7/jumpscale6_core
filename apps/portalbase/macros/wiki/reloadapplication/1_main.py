def main(j, args, params, tags, tasklet):
    params.merge(args)

    # temporary hack to get the application name
    name = j.system.fs.getParentDirName(j.system.fs.getParent(j.core.portal.active.cfgdir))
    j.core.portal.active.restartInProcess(name)

    params.result = ("", params.doc)


def match(j, args, params, tags, tasklet):
    return True

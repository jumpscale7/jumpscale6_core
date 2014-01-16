def main(j, args, params, tags, tasklet):
    params.merge(args)

    # temporary hack to get the application name
    j.core.portal.runningPortal.restartInProcess('')

    params.result = ("", params.doc)


def match(j, args, params, tags, tasklet):
    return True


def main(o, args, params, tags, tasklet):

    page = args.page

    from pylabs.Shell import ipshellDebug, ipshell
    print "DEBUG NOW MACRO, do ctrl D when done."
    ipshell()

    params.result = page
    return params


def match(o, args, params, tags, tasklet):
    return True

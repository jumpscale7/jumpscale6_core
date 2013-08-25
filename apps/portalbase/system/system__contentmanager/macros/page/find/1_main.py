
def main(o, args, params, tags, tasklet):
    page = args.page
    page.addBootstrap()
    page.hasfindmenu = True
    page._hasmenu = True
    params.result = page
    return params


def match(o, args, params, tags, tasklet):
    return True

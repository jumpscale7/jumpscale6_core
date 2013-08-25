
def main(o, args, params, tags, tasklet):

    page = args.page

    modifier = j.html.getPageModifierGridDataTables(page)
    page = modifier.addTable(args.tags.tagGet("url"))

    params.result = page
    return params


def match(o, args, params, tags, tasklet):
    return True

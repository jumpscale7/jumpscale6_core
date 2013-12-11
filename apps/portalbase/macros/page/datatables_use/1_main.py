
def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    tags = args.tags

    modifier = j.html.getPageModifierGridDataTables(args.page)
    params.result = modifier.prepare4DataTables()

    return params


def match(j, args, params, tags, tasklet):
    return True

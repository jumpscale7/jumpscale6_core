
def main(q,args,params,tags,tasklet):
    params.result = page = args.page
    tags = args.tags

    modifier = q.html.getPageModifierGridDataTables(args.page)
    params.result = modifier.prepare4DataTables()
    
    return params


def match(q,args,params,tags,tasklet):
    return True


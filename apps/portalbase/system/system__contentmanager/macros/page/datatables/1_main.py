
def main(q,args,params,tags,tasklet):

    page = args.page

    modifier=q.html.getPageModifierGridDataTables(page)
    page=modifier.addTable(args.tags.tagGet("url"))

    params.result = page 
    return params


def match(q,args,params,tags,tasklet):
    return True


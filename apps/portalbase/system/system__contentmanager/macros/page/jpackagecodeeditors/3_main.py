def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    if version:
        package = j.packages.find(domain, name, version)[0]
    else:
        package = j.packages.findNewest(domain, name)
    
    page.addHeading("Code editors for %s:%s"%(package.domain,package.name), 2)

    for path in package.getCodeLocationsFromRecipe():
        page.addHeading("%s"%path, 3)
        page.addExplorer(path,readonly=False, tree=True,height=300)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

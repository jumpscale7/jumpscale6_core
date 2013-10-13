def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    if version:
        package = j.packages.find(domain, name, version)[0]
    else:
        package = j.packages.findNewest(domain, name)
    
    page.addHeading("JPackage '%s' Tasklets" % package.name, 2)
    page.addExplorer(package.getPathMetadata())

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

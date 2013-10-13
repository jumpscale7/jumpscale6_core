def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    if version:
        package = j.packages.find(domain, name, version)[0]
    else:
        package = j.packages.findNewest(domain, name)
    
    page.addHeading(package.name, 2)
    info = ('domain', 'version', 'buildNr', 'description', 'taskletsChecksum')
    for i in info:
        page.addHTML('%s: %s' % (i, getattr(package, i)))

    page.addHTML('Dependencies:')
    for dep in package.getDependencies():
        page.addLink(dep.name, '/system/JPackageShow?domain=%s&name=%s&version=%s' % (dep.domain, dep.name, dep.version))

    page.addHTML('Supported platforms: %s' % ', '.join([x for x in package.supportedPlatforms]))

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

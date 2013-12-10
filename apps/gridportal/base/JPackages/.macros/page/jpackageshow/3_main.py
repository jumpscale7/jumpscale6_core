def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    if version:
        package = j.packages.find(domain, name, version)[0]
    else:
        if domain and name:
            package = j.packages.findNewest(domain, name)
        else:
            returnpath = "/jpackages/jpackages"
            returncontent = "<script>window.open('%s', '_self', '');</script>" % returnpath
            page.addHTML(returncontent)
            params.result = page
            return params
    
    page.addHeading(package.name, 2)
    page.addHTML('Installed: %s' % (package.isInstalled()))
    info = ('domain', 'version', 'buildNr', 'description')
    for i in info:
        page.addHTML('%s: %s' % (i.capitalize(), getattr(package, i)))

    page.addHTML('Dependencies:')
    dependencies = sorted(package.getDependencies(), key=lambda x: x.name)
    for dep in dependencies:
        href = '/jpackages/JPackageShow?domain=%s&name=%s&version=%s' % (dep.domain, dep.name, dep.version)
        page.addBullet("<a href='%s'>%s</a>" % (href, dep.name))

    page.addHTML('Supported platforms: %s' % ', '.join([x for x in package.supportedPlatforms]))

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

def main(j, args, params, tags, tasklet):

    page = args.page

    def _getDomainPackages(d):
        page.addHeading(d.domainname, 2)
        for p in d.getJPackages():
            page.addLink(p.name, '/system/JPackageShow?domain=%s&name=%s&version=%s' % (d.domainname, p.name, p.version))

    domain = args.tags.tagGet('domain', '')
    if not domain:
        #return all packages
        for d in j.packages.domains:
            _getDomainPackages(d)

    else:
        #return packages of domain
        d = j.packages.getDomainObject(domain)
        _getDomainPackages(d)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

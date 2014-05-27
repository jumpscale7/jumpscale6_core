def main(j, args, params, tags, tasklet):

    page = args.page
    attributes = "class='nav nav-list' style='-moz-column-count: 3; -webkit-column-count:3; column-count:3;'"

    domain = args.tags.tagGet('domain', '')
    nid = args.tags.tagGet('nid', j.application.whoAmI.nid)
    jpackagelist = j.apps.system.packagemanager.getJPackages(domain=domain, nid=nid)
    if not jpackagelist:
        page.addMessage('No JPackages to display. Make sure your processmanager and workers are running')
        params.result = page
        return params

    jpackages = dict()
    for jp in jpackagelist:
        if jp['domain'] not in jpackages:
            jpackages[jp['domain']] = list()
        jpackages[jp['domain']].append(jp)
  
    for domain in sorted(jpackages.keys()):
        page.addHeading(domain, 2)
        for jp in sorted(jpackages[domain], key=lambda x: x['name'].lower()):
            href = '/jpackages/JPackageShow?domain=%s&name=%s&version=%s' % (domain, jp['name'], jp['version'])
            icon = 'icon-ok' if jp['installed'] else 'icon-remove'
            page.addBullet("<a href='%s'><i class='%s'></i> %s</a>" % (href, icon, jp['name']), attributes=attributes)

        

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

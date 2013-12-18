def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nodeId')

    j.core.portal.runningPortal.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        _, nid, _ = j.application.whoAmI
    result = j.apps.system.packagemanager.getJPackage(nodeId=nid, domain=domain, pname=name, version=version)

    import json
    result = json.loads(result['result'])['result']
    if result == False:
        page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
        params.result = page
        return params
    
    
    page.addHeading(result['name'], 2)
    page.addHTML('Installed: %s' % (result['isInstalled']))
    info = ('domain', 'version', 'buildNr', 'description')
    for i in info:
        page.addHTML('%s: %s' % (i.capitalize(), result[i]))

    page.addHTML('Dependencies:')
    dependencies = sorted(result['dependencies'], key=lambda x: x.name)
    for dep in dependencies:
        href = '/jpackages/JPackageShow?domain=%s&name=%s&version=%s' % (dep.domain, dep.name, dep.version)
        page.addBullet("<a href='%s'>%s</a>" % (href, dep.name))

    page.addHTML('Supported platforms: %s' % ', '.join([x for x in result['supportedPlatforms']]))

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

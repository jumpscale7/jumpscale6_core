def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    if not nid:
        nid = j.application.whoAmI.nid
    result = j.apps.system.packagemanager.getJPackageInfo(nid=nid, domain=domain, pname=name, version=version)
    
    if result == False:
        page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
        params.result = page
        return params
   
    page.addHeading("Code editors for %s:%s"%(result['domain'], result['name']), 2)

    for path in result['codeLocations']:
        page.addHeading("%s"%path, 3)
        page.addExplorer(path,readonly=False, tree=True,height=300)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

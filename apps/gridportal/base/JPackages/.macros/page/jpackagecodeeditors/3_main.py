def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nodeId')

    j.core.portal.runningPortal.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        _, nid, _ = j.application.whoAmI
    result = j.apps.system.packagemanager.getJPackage(nodeId=nid, domain=domain, pname=name, version=version)['result']

    import json
    result = json.loads(result)['result']
    
    if result == False:
        page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
        params.result = page
        return params
    
    page.addHeading("Code editors for %s:%s"%(result['domain'], result['name']), 2)

    for path in result['getCodeLocationsFromRecipe']:
        page.addHeading("%s"%path, 3)
        page.addExplorer(path,readonly=False, tree=True,height=300)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

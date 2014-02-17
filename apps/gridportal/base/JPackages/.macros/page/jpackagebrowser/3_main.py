def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    if not nid:
        nid = j.application.whoAmI.nid
    result = j.apps.system.packagemanager.getJPackageInfo(nid=nid, domain=domain, pname=name, version=version)

    if result==None:
        page.addHeading("could not find package:%s %s (%s) on node %s"%(domain,name,version,nid), level=4)
        params.result = page
        return params

    if result == False:
        page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
        params.result = page
        return params
   
    page.addExplorer(result['metadataPath'],readonly=False, tree=True)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

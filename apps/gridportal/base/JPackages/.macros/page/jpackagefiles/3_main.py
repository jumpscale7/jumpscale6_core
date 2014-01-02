def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    j.core.portal.runningPortal.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        _, nid, _ = j.application.whoAmI
    result = j.apps.system.packagemanager.getBlobs(nid=nid, domain=domain, pname=name, version=version)['result']

    import json
    blobs = json.loads(result)['result']
    if blobs == False:
        page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
        params.result = page
        return params

    page.addHeading('Files', 2)
    modifier = j.html.getPageModifierGridDataTables(page)

    for blob in blobs:
        platform = blob['platform']
        ttype = blob['ttype']

        page.addHeading("Platform:%s" % platform.capitalize(), 5)

        url = '/restmachine/system/packagemanager/getBlobContents?nid=%s&domain=%s&pname=%s&version=%s&platform=%s&ttype=%s' % (nid, domain, name, version, platform, ttype)

        fieldnames = ('File', 'MD5 Checksum')
        page = modifier.addTableFromURL(url, fieldnames)

    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True

def main(j, args, params, tags, tasklet):

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    j.core.portal.active.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        nid = j.application.whoAmI.nid
    result = j.apps.system.packagemanager.getJPackageFilesInfo(nid=nid, domain=domain, pname=name, version=version)

    if not result:
        out = 'Could not find jpackage files'
        params.result = (out, args.doc)
        return params

    out = "h1. Files\n"
    out += '||Platform||Type||FileName||MD5Sum||\n'
    for platform, ttype, filename, md5sum in result:
        out+= '|%s|%s|%s|%s|\n' % (platform, ttype, filename, md5sum)

    params.result = (out, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True

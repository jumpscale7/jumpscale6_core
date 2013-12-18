from JumpScale import j

descr = """gets jpackage info"""

name = "jpackage_info"
category = "jpackages"
organization = "jumpscale"
author = "khamisr@incubaid.com"
version = "1.0"

gid, nid, _ = j.application.whoAmI
roles = ["node.%s.%s" % (gid, nid)]


def action(domain, pname, version):
    
    if version and domain and pname:
        package = j.packages.find(domain, pname, version)[0]
    else:
        if domain and pname:
            package = j.packages.findNewest(domain, pname)
            if not package:
                return False
        else:
            return False

    packagedata = {}
    info = ('domain', 'version', 'buildNr', 'description', 'name', 'dependencies', 'supportedPlatforms')
    for i in info:
        packagedata[i] = getattr(package, i)
    packagedata['isInstalled'] = package.isInstalled()
    packagedata['getCodeLocationsFromRecipe'] = package.getCodeLocationsFromRecipe()
    packagedata['getPathMetadata'] = package.getPathMetadata()
    return packagedata
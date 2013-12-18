from JumpScale import j

descr = """gets jpackage info"""

name = "jpackage_blobdata"
category = "jpackages"
organization = "jumpscale"
author = "khamisr@incubaid.com"
version = "1.0"

gid, nid, _ = j.application.whoAmI
roles = ["node.%s.%s" % (gid, nid)]


def action(domain, pname, version, platform, ttype):
    
    if version and domain and pname:
        package = j.packages.find(domain, pname, version)[0]
    else:
        if domain and pname:
            package = j.packages.findNewest(domain, pname)
            if not package:
                return False
        else:
            return False

    blobinfo = package.getBlobInfo(platform, ttype)

    aaData = list()
    for entry in blobinfo[1]:
        itemdata = list()
        itemdata.append(entry[1])
        itemdata.append(entry[0])
        aaData.append(itemdata)

    return {'aaData': aaData}

    return blobinfo
from JumpScale import j

descr = """gets jpackage description"""

name = "jpackage_descr"
category = "jpackages"
organization = "jumpscale"
author = "rkhamis@incubaid.com"
version = "1.0"

gid, nid, _ = j.application.whoAmI
roles = ["node.%i.%i" % (gid, nid)]


def action(domain, pname, version):
    j.packages.docGenerator.getDocs()

    if  not domain or not pname or not j.packages.docGenerator.docs.existsPackage(domain, pname, version):
        out="ERROR:COULD NOT FIND PACKAGE:%s %s %s"%(domain, pname, version)
        return out

    jp=j.packages.docGenerator.docs.getPackage(domain, pname, version)

    out=jp.getDescr()

    return out

from JumpScale import j

descr = """gets jpackage info filenames"""

name = "jpackage_blobs"
category = "jpackages"
organization = "jumpscale"
author = "khamisr@incubaid.com"
version = "1.0"

gid, nid, _ = j.application.whoAmI
roles = ["node.%s.%s" % (gid, nid)]


def action(domain, pname, version):
    
    if domain and pname and version:
        blobpaths = j.system.fs.joinPaths(j.dirs.packageDir, "metadata", domain, pname, version, "files")
        if not j.system.fs.exists(blobpaths):
            return False
        blobs = j.system.fs.find(blobpaths, '*.info')
        infofiles = []
        for blob in blobs:
            platform = blob.split('___')[0]
            ttype = blob.split('___')[1].split('.info')[0]
            infofiles.append({'platform': platform, 'ttype': ttype})
        return infofiles
    else:
        returnpath = "/jpackages/jpackages"
        returncontent = "<script>window.open('%s', '_self', '');</script>" % returnpath
        return returncontent
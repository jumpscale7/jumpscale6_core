from JumpScale import j

descr = """starts jpackage"""

name = "start_jpackage"
category = "jpackages"
organization = "jumpscale"
author = "zains@incubaid.com"
version = "1.0"
roles = ["computenode"]


def action(domain, pname):
    
    package = j.packages.findNewest(domain, pname, returnNoneIfNotFound=True)
    if package:
        package.start()
        return True
    else:
        return False
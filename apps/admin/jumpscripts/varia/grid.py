
from JumpScale import j

descr = """
deploy grid
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.grid"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi

    if node.args.gridnr =="":
        node.args.gridnr=j.console.askString("Grid id, make sure is unique.")

    cmd="jsconfig hrdset -n grid.id -v %s"%node.args.gridnr
    print c.run(cmd)

    cmd="jsconfig hrdset -n grid.master.superadminpasswd -v %s"%j.tools.hash.md5_string(node.args.passwd)
    print c.run(cmd)
    
    cmd="jsconfig hrdset -n gridmaster.grid.id -v %s"%node.args.gridnr
    print c.run(cmd)

    cmd="jsconfig hrdset -n elasticsearch.cluster.name -v cl_%s"%node.args.gridnr
    print c.run(cmd)

    print c.run("jpackage install -n sentry -r")
    print c.run("jsprocess start -n sentry")

    print c.run("jpackage install -n elasticsearch -r")
    print c.run("jpackage install -n osis -r --debug")
    print c.run("jsprocess start -c")
    print c.run("jpackage install -n grid -r --debug")
    print c.run("jpackage install -n grid_master -r --debug")
    print c.run("jpackage install -n grid_node -r --debug")
    print c.run("jsprocess start -c")

    #@todo should run but now die
    # print c.run("jsprocess disable -n logger")

    print c.run("jsuser add -d admin:admin:admin::incubaid")

    print c.run("jpackage install -n grid_portal -r --debug")
    print c.run("jpackage install -n portal -r --debug")
    print c.run("jpackage install -n agentcontroller -r --debug")
    print c.run("jpackage install -n workers -r --debug")
    print c.run("jsprocess start -c")

    print c.run("jpackage install -n blobserver2 -r --debug")
    print c.run("jpackage install -n jumpscale_examples -r --debug")
    print c.run("jpackage install -n doc_jumpscale -r --debug")

    print c.run("jpackage install -n shorewall")
    print c.run("shorewall stop")

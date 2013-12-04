from JumpScale import j

j.application.appname = "autostarter"
j.application.start()


from optparse import OptionParser

parser = OptionParser()
parser.add_option('-r', '--remote', help='Ip address of node',default="")
parser.add_option('-s', '--seedpasswd', help='Originalpasswd (used to login first time)',default="")
parser.add_option('-p', '--passwd', help='New Passwd To Set Or Use',default="rooter")
parser.add_option('-g', '--gridnr', help='Id of grid, make sure is unique.',default="")

(options, args) = parser.parse_args()


if options.remote =="":
    options.remote=j.console.askString("Ip address of remote")

if options.seedpasswd =="":
    options.seedpasswd=j.console.askString("Seedpasswd if any, press enter if none.",defaultparam="")

if options.passwd =="":
    options.passwd=j.console.askString("New Passwd To Set Or Use (default rooter)",defaultparam="rooter")

if options.gridnr =="":
    options.gridnr=j.console.askString("Grid id, make sure is unique.")

remote = options.remote
seedpasswd = options.seedpasswd
passwd = options.passwd


import JumpScale.baselib.remote

### FIRST DO
help="""
#On a live system using systemd: (2012.10.06 or later) do
systemctl start sshd
rc.d start sshd
passwd
"""
print help

cuapi = j.remote.cuisine.api
j.remote.cuisine.fabric.env["password"]=passwd
cuapi.connect(remote)

#this will make sure new password is set
cl=j.tools.expect.new("sh")
cl.login(remote=remote,passwd=passwd,seedpasswd=seedpasswd)

def prepare_platform():
    print cuapi.apt_get("update")
    print cuapi.apt_get("upgrade")
    print cuapi.apt_get("install mercurial ssh python2.7 python-apt openssl ca-certificates python-pip ipython mc -y")
    

def install_jscore():
    try:
        print cuapi.run("pip uninstall JumpScale-core -y")
    except:
        pass
    print cuapi.run("pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip")
    print cuapi.dir_ensure("/opt/jumpscale/cfg/jsconfig/", True)    
    print cuapi.dir_ensure("/opt/jumpscale/cfg/jpackages/", True)
    print cuapi.file_upload("/opt/jumpscale/cfg/jsconfig/blobstor.cfg","/opt/jumpscale/cfg/jsconfig/blobstor.cfg" )
    print cuapi.file_upload("/opt/jumpscale/cfg/jsconfig/bitbucket.cfg", "/opt/jumpscale/cfg/jsconfig/bitbucket.cfg")
    print cuapi.file_upload("/opt/jumpscale/cfg/jpackages/sources.cfg","/opt/jumpscale/cfg/jpackages/sources.cfg")
    print cuapi.run("jpackage_update")
    try:
        print cuapi.run("jscode_update")
    except:
        pass    
    print cuapi.run("jpackage_install -n core -r --debug")

def install_grid():
    print cuapi.dir_ensure("/opt/jumpscale/cfg/hrd/", True)
    
    hrd=j.core.hrd.getHRD("cfg/hrd")

    
    hrd.set("grid.id",options.gridnr)
    hrd.set("gridmaster.grid.id",options.gridnr)
    hrd.set("elasticsearch.cluster.name","cl_%s"%options.gridnr)

    names= [j.system.fs.getBaseName(item)[:-4] for item in j.system.fs.listFilesInDir("cfg/hrd") if item.find(".hrd")<>-1]
    
    for hrdname in names:
        print cuapi.file_upload("/opt/jumpscale/cfg/hrd/", "cfg/hrd/%s.hrd"%hrdname)


    print cuapi.run("jpackage_install -n elasticsearch -r")
    print cuapi.run("jpackage_install -n osis -r --debug")
    print cuapi.run("jsprocess_start")
    print cuapi.run("jpackage_install -n grid -r --debug")
    print cuapi.run("jpackage_install -n grid_master -r --debug")
    print cuapi.run("jpackage_install -n grid_node -r --debug")
    print cuapi.run("jpackage_install -n logger -r --debug")
    print cuapi.run("jsprocess_start")
    print cuapi.run("jpackage_install -n grid_portal -r --debug")
    print cuapi.run("jpackage_install -n portal -r --debug")
    print cuapi.run("jpackage_install -n agentcontroller -r --debug")
    print cuapi.run("jpackage_install -n agent -r --debug")
    print cuapi.run("jsprocess_start")

def install_desktop():
    names=["xfce4desktop","xrdp","kingsoftoffice","sparkgateway"]
    for name in names:
        print c.run("jpackage_install -n %s"%name)


# prepare_platform()
# install_jscore()
# install_grid()
install_desktop

# print c.run("")


##EXAMPLES
# cl.expect("#",timeout=0.5)
# cl.executeStep("echo Y | pacman %s\n"%cmd,"#")
# c.process_kill("pacman")
# c.run(cmd)
# c.file_unlink("/mnt/var/lib/pacman/db.lck")    



# for item in ["sparkgateway","grid_portal","logger","elasticsearch","agentcontroller","osis"]:
#     j.packages.findByName(item)[0].configure()



j.application.stop()



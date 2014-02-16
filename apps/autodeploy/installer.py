from JumpScale import j

j.application.appname = "jumpscale:autodeploy_installer"
j.application.start()


from optparse import OptionParser

parser = OptionParser()
parser.add_option('-r', '--remote', help='Ip address of node',default="")
parser.add_option('-l', '--local', action='store_true', help='To execute locally.')
parser.add_option('-s', '--seedpasswd', help='Originalpasswd (used to login first time)',default="")
parser.add_option('-p', '--passwd', help='New Passwd To Set Or Use',default="rooter")
parser.add_option('-g', '--gridnr', help='Id of grid, make sure is unique.',default="")
parser.add_option('-c', '--cfgname', help='Name of cfg directory.',default="")
parser.add_option('-t','--type', help='Type of action (platform,core,desktop,grid), is comma separated.',default="")
parser.add_option('--nopasswd', help='work with ssh key',default=False)

(options, args) = parser.parse_args()

if options.local:
    options.remote="127.0.0.1"
    options.seedpasswd=""

else:
    if options.remote =="":
        options.remote=j.console.askString("Ip address of remote")

    if options.seedpasswd =="":
        options.seedpasswd=j.console.askString("Seedpasswd if any, press enter if none.",defaultparam="")

if options.gridnr =="":
    options.gridnr=j.console.askString("Grid id, make sure is unique.")

if options.passwd =="":
    options.passwd=j.console.askString("New Passwd To Set Or Use (default rooter)",defaultparam="rooter")

remote = options.remote
seedpasswd = options.seedpasswd
passwd = options.passwd

if options.cfgname=="":
    options.cfgname=j.console.askChoice(j.system.fs.listDirsInDir("cfgs",False,True),"Please select configuration templates for the remote machine.")

import JumpScale.baselib.remote

### FIRST DO
help="""
#On a live system using systemd: (2012.10.06 or later) do
systemctl start sshd
rc.d start sshd
passwd
"""
print help


if options.type=="":
    result=j.console.askChoiceMultiple(["platform","core","configure","grid","desktop"])
else:
    result=options.type.split(",")

cuapi = j.remote.cuisine.api
if options.nopasswd==False:
    j.remote.cuisine.fabric.env["password"]=passwd
cuapi.connect(remote)

def setpasswd():
    #this will make sure new password is set
    cl=j.tools.expect.new("sh")
    cl.login(remote=remote,passwd=passwd,seedpasswd=seedpasswd)

if options.nopasswd==False:
    setpasswd()

def prepare_platform():
    print cuapi.apt_get("update")
    print cuapi.apt_get("upgrade")
    print cuapi.apt_get("install mercurial ssh python2.7 python-apt openssl ca-certificates python-pip ipython mc -y")
    
def install_jscore():
    try:
        print cuapi.run("pip uninstall JumpScale-core -y")
    except:
        pass
    print cuapi.run("pip install https://bitbucket.org/jumpscale/jumpscale_core/get/unstable.zip")
    install_configure()

def install_configure():

    items=j.system.fs.listFilesInDir("cfgs/%s"%options.cfgname,True)
    done=[]
    for item in items:
        cfgdirpath=j.system.fs.getDirName(j.system.fs.pathRemoveDirPart(item,"cfgs/%s"%options.cfgname)).rstrip("/")
        if cfgdirpath not in done:
            print cuapi.dir_ensure("/opt/jumpscale/cfg/%s"%cfgdirpath, True)
            done.append(cfgdirpath)            
        cuapi.file_upload("/opt/jumpscale/cfg/%s/%s"%(cfgdirpath,j.system.fs.getBaseName(item)),item)#,True,True)

    cmd="jsconfig hrdset -n system.superadmin.passwd -v %s"%passwd
    print cuapi.run(cmd)            

    print cuapi.run("jpackage mdupdate")
    try:
        print cuapi.run("jscode update -f -a* -r*")
    except:
        pass    
    print cuapi.run("jpackage install -n core -r --debug")

def install_grid():

    cmd="jsconfig hrdset -n grid.id -v %s"%options.gridnr
    print cuapi.run(cmd)

    cmd="jsconfig hrdset -n grid.master.superadminpasswd -v %s"%j.tools.hash.md5_string(passwd)
    print cuapi.run(cmd)
    
    cmd="jsconfig hrdset -n gridmaster.grid.id -v %s"%options.gridnr
    print cuapi.run(cmd)

    cmd="jsconfig hrdset -n elasticsearch.cluster.name -v cl_%s"%options.gridnr
    print cuapi.run(cmd)

<<<<<<< local
=======
    cmd="jsconfig hrdset -n agent.nrinstances -v %s"%2
    print cuapi.run(cmd)

    print cuapi.run("jpackage install -n sentry -r")
    print cuapi.run("jsprocess start -n sentry")

>>>>>>> other
    print cuapi.run("jpackage install -n elasticsearch -r")
    print cuapi.run("jpackage install -n osis -r --debug")
    print cuapi.run("jsprocess start -c")
    print cuapi.run("jpackage install -n grid -r --debug")
    print cuapi.run("jpackage install -n grid_master -r --debug")
    print cuapi.run("jpackage install -n grid_node -r --debug")
    print cuapi.run("jsprocess start -c")

    print cuapi.run("jpackage install -n grid_portal -r --debug")
    print cuapi.run("jpackage install -n portal -r --debug")
    print cuapi.run("jpackage install -n agentcontroller -r --debug")
    print cuapi.run("jpackage install -n workers -r --debug")
    print cuapi.run("jsprocess start -c")

    print cuapi.run("jpackage install -n blobserver2 -r --debug")
    print cuapi.run("jpackage install -n jumpscale_examples -r --debug")
    print cuapi.run("jpackage install -n doc_jumpscale -r --debug")

    print cuapi.run("jpackage install -n shorewall")
    print cuapi.run("shorewall stop")

def install_desktop():

    names=["xfce4desktop","xrdp","kingsoftoffice","sparkgateway","sublimetext"]
    # names=["xfce4desktop","xrdp"]
    for name in names:
        print cuapi.run("jpackage install -n %s -r"%name)
    cmd='update-rc.d xrdp defaults'
    print cuapi.run(cmd)


if "platform" in result:
    prepare_platform()

if "core" in result:
    install_jscore()

if "configure" in result and not "core" in result:
    install_configure()

if "grid" in result:
    install_grid()

if "desktop" in result:
    install_desktop()

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



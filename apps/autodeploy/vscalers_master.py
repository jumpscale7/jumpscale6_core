from JumpScale import j

j.application.appname = "jumpscale:autodeploy_installer"
j.application.start()
import time

from optparse import OptionParser

parser = OptionParser()
parser.add_option('-r', '--remote', help='Ip address of node',default="")
parser.add_option('-l', '--local', action='store_true', help='To execute locally.')
parser.add_option('-p', '--passwd', help='New Passwd To Set Or Use',default="rooter")
parser.add_option('--nopasswd', help='work with ssh key',default=False)
parser.add_option('--ipaddr', help='ipaddr with mask',default="10.101.175.200/16")



(options, args) = parser.parse_args()

if options.local:
    options.remote="127.0.0.1"
    options.seedpasswd=""

else:
    if options.remote =="":
        options.remote=j.console.askString("Ip address of remote")

if options.passwd =="":
    options.passwd=j.console.askString("Passwd",defaultparam="rooter")

remote = options.remote
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
if options.nopasswd==False:
    j.remote.cuisine.fabric.env["password"]=passwd
cuapi.connect(remote)

def install_lxc():
    ipaddr,mask=options.ipaddr.split("/")
    mask=int(mask)

    update=True
    updateimage=True
    base=True
    master=True

    if update:
        print cuapi.run("jscode update -a jumpscale -r unstable__jumpscale_core -u -f")
        print cuapi.run("jpackage install -n libs -r --debug")
        print cuapi.run("jscode update -a jumpscale -r unstable__jumpscale_lib -u -f")    
        print cuapi.run("jpackage link -n core")
        print cuapi.run("apt-get install lxc cloud-utils python-netaddr -y")
        print cuapi.run("jpackage mdupdate")

    if updateimage:
        print cuapi.run("rm -rf /var/lib/lxc/saucy-amd64-base")
        print cuapi.run("lxc-create -n saucy-amd64-base -t ubuntu-cloud -- --release=saucy --arch=amd64")      
        #print cuapi.run("jpackage install -n lxc -r") #this will reset the interfaces & put std briding config on it (DANGEROUS)
        print cuapi.run("jpackage download -n lxc --copy") #this will only copy the files

    # #install ssh in saucy-base
    # print cuapi.run("rm -f /var/lib/lxc/saucy-amd64-base/rootfs/etc/resolv.conf")
    # print cuapi.run("cp /etc/resolv.conf /var/lib/lxc/saucy-amd64-base/rootfs/etc/resolv.conf")
    # print cuapi.run("chroot /var/lib/lxc/saucy-amd64-base/rootfs apt-get install ssh")
    
    cmd='ssh-keygen -f "/root/.ssh/known_hosts" -R '+str(ipaddr) #make sure there is no old ssh stuff unside
    j.system.process.executeWithoutPipe(cmd)

    if base:
        print cuapi.run("jsmachine new -n base -b saucy-amd64-base --start --pubip=%s/%s"%(ipaddr,mask))
        cmd="python vscalers_basenode.py -r %s -p rooter -s rooter -g 241 -c vscalers_computenode -t platform,core,configure"%ipaddr
        j.system.process.executeWithoutPipe(cmd)

        #commando's to do in base
        def do(cmd):
            print cuapi.run("jsmachine cmd -n base -c '%s'"%cmd)
        do("jscode update -f -a* -r*")
        do("jpackage install -n libs -r --debug")

        print cuapi.run("jsmachine stop -n base")

    if master:
        print cuapi.run("jsmachine new -n gridmaster -b mach_base --pubip=%s/%s"%(ipaddr,mask))
        print cuapi.run("jsmachine start -n gridmaster")




install_lxc()

j.application.stop()
    
def install_jscore():
    try:
        print cuapi.run("pip uninstall JumpScale-core -y")
    except:
        pass
    print cuapi.run("pip install https://bitbucket.org/jumpscale/jumpscale_core/get/unstable.zip")
    install_configure()

    print cuapi.run("jpackage mdupdate")
    try:
        print cuapi.run("jscode update -f -a* -r*")
    except:
        pass    
    print cuapi.run("jpackage install -n core -r --debug")

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

def install_grid():

    cmd="jsconfig hrdset -n grid.id -v %s"%options.gridnr
    print cuapi.run(cmd)

    cmd="jsconfig hrdset -n grid.master.superadminpasswd -v %s"%j.tools.hash.md5_string(passwd)
    print cuapi.run(cmd)
    
    cmd="jsconfig hrdset -n gridmaster.grid.id -v %s"%options.gridnr
    print cuapi.run(cmd)

    cmd="jsconfig hrdset -n elasticsearch.cluster.name -v cl_%s"%options.gridnr
    print cuapi.run(cmd)

    print cuapi.run("jpackage install -n sentry -r")
    print cuapi.run("jsprocess start -n sentry")

    print cuapi.run("jpackage install -n elasticsearch -r")
    print cuapi.run("jpackage install -n osis -r --debug")
    print cuapi.run("jsprocess start -c")
    print cuapi.run("jpackage install -n grid -r --debug")
    print cuapi.run("jpackage install -n grid_master -r --debug")
    print cuapi.run("jpackage install -n grid_node -r --debug")
    print cuapi.run("jsprocess start -c")

    #@todo should run but now die
    # print cuapi.run("jsprocess disable -n logger")

    print cuapi.run("jsuser add -d admin:admin:admin::incubaid")

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


j.application.stop()



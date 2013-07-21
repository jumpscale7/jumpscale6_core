import sys
sys.path.insert(0,'../lib')

from OpenWizzy import *

import OpenWizzy.baselib.platforms #gets access to ubuntu code
import OpenWizzy.baselib.owdeveltools

do=o.system.installtools

o.application.start("owinstaller",basedir="/opt/openwizzy6/",appdir="/opt/openwizzy6/apps/exampleapp/")

if o.system.platformtype.isLinux():
    o.system.platform.ubuntu.check()


    def installpackages():
        do.execute("apt-get update")
        # do.execute("apt-get upgrade -y")
        debpackages = ('python2.7','nginx', 'curl', 'mc', 'ssh', 'mercurial', 'python-gevent', 'python-simplejson', 'python-numpy',
                        'byobu', 'python-apt','ipython','python-pip','python-imaging','python-requests',"python-paramiko","gcc","g++","python-dev","python-zmq","msgpack-python") 

        for name in debpackages:
            print "check install %s"%name
            o.system.platform.ubuntu.install(name)

        do.execute("easy_install urllib3")
        do.execute("easy_install ujson")
        do.execute("easy_install blosc")
        do.execute("easy_install urllib3")


    installpackages()

    # pythpath="/usr/lib/python2.7/"
    # if not o.system.fs.exists(pythpath):
    #     raise RuntimeError("Could not find python 2.7 env on %s"%pythpath)

    o.develtools.installer.link2code()

    # owdir="%s/OpenWizzy"%pythpath
    # do.createdir(owdir)

    # do.copydeletefirst("%s/__init__.py"%o.dirs.libDir,"%s/__init__.py"%owdir)
    # srcdir=o.dirs.libDir
    # for item in ["base","baselib","core"]:
    #     do.symlink("%s/%s"%(srcdir,item),"%s/%s"%(owdir,item))  

    # do.createdir("%s/%s"%(o.dirs.baseDir,"apps"))

    # src="%s/../../shellcmds"%o.dirs.libDir
    # dest="%s/shellcmds"%o.dirs.baseDir
    # do.symlink(src,dest)  

    # for item in o.system.fs.listFilesInDir(dest,filter="ow*.py"):
    #     C="python %s/%s $@"%(dest,o.system.fs.getBaseName(item))
    #     path="/usr/bin/%s"%o.system.fs.getBaseName(item).replace(".py","")
    #     o.system.fs.writeFile(path,C)
    #     cmd='chmod 777 %s'%path
    #     o.system.process.execute(cmd)

else:
    raise RuntimeError("Openwizzy 6 is for now only supported on ubuntu or mint.")

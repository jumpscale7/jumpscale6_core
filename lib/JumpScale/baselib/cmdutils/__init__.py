from JumpScale import j

import JumpScale.baselib.jpackages #load jpackages

import argparse
import sys

class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
           self._print_message(message, sys.stderr) 
        if j.application.state == j.enumerators.AppStatusType.RUNNING:
            j.application.stop(status)
        else:
            sys.exit(status)


def processLogin(parser):

    parser.add_argument("-l",'--login', help='login for grid, if not specified defaults to root')
    parser.add_argument("-p",'--passwd', help='passwd for grid')
    parser.add_argument("-a",'--addr', help='ip addr of master, if not specified will be the one as specified in local config')

    opts = parser.parse_args()

    if opts.login==None:
        opts.login="root"

    if opts.passwd==None and opts.login=="root":
        if j.application.config.exists("grid.master.superadminpasswd"):
            opts.passwd=j.application.config.get("grid.master.superadminpasswd")
        else:
            opts.passwd=j.console.askString("please provide superadmin passwd for the grid.")

    if opts.addr==None:    
        opts.addr=j.application.config.get("grid.master.ip")

    return opts


def getJPackage(args, installed=None,domain=None,debug=None):
    if installed:
        domain=""

    if args.domain<>None:
        domain=args.domain

    if args.name==None:
        args.name=""
    else:
        if domain==None:
            domain=""
    packagesall=[]
    for pname in args.name.split(","):
        if pname<>"":
                packages = j.packages.find(name=pname, domain=domain, version=args.version,installed=False)
        else:
            packages = j.packages.find(name=pname, domain=domain, version=args.version,installed=installed)

        if debug==False and pname=="":
            debugpackages=j.packages.getDebugPackages()
            packages=[item for item in packages if item not in debugpackages]        

        if len(packages) == 0:
            if installed:
                print "Could not find package with name '%s' in domain '%s' with version '%s' which is installed." % (pname, domain, args.version)
            else:
                print "Could not find package with name '%s' in domain '%s' with version '%s'" % (pname, domain, args.version)
            j.application.stop(1)
        elif len(packages) > 1 and pname.find("*"):
            pass #no need to ask interactive
        elif len(packages) > 1:
            if not j.application.shellconfig.interactive:
                print "Found multiple packages %s" % (packages)
                j.application.stop(1)
            else:
                packages = j.console.askChoiceMultiple(packages, "Multiple packages found. Select:")

        if args.deps:
            for p in packages:
                for dep in p.getDependencies():
                    if dep not in packages:
                        packages.append(dep)
        packagesall+=packages
    
    return packagesall

def getProcess(parser=None):
    parser = parser or ArgumentParser()
    parser.add_argument('-d', '--domain', help='Process domain name')
    parser.add_argument('-n', '--name', help='Process name')
    return parser.parse_args()

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
        if j.application.config.exists("gridmaster.superadminpasswd"):
            opts.passwd=j.application.config.get("gridmaster.superadminpasswd")
        else:
            opts.passwd=j.console.askString("please provide superadmin passwd for the grid.")

    if opts.addr==None:    
        opts.addr=j.application.config.get("grid.master.ip")

    return opts


def getJPackage(parser=None,installed=None,domain=None):
    if installed:
        domain=""
    parser = parser or ArgumentParser()
    parser.add_argument('-n','--name',required=False, help='Name of jpackage to be installed')
    parser.add_argument('-d','--domain',required=False, help='Name of jpackage domain to be installed')
    parser.add_argument('-v','--version',required=False, help='Version of jpackage to be installed')

    args = parser.parse_args()

    if args.domain<>None:
        domain=args.domain

    if args.name==None:
        args.name=""
    else:
        if domain==None:
            domain=""

    if args.name<>"":
        packages = j.packages.find(name=args.name, domain=domain, version=args.version,installed=False)
    else:
        packages = j.packages.find(name=args.name, domain=domain, version=args.version,installed=installed)


    if len(packages) == 0:
        if installed:
            print "Could not find package with name '%s' in domain '%s' with version '%s' which is installed." % (args.name, domain, args.version)
        else:
            print "Could not find package with name '%s' in domain '%s' with version '%s'" % (args.name, domain, args.version)
        j.application.stop(1)
    elif len(packages) > 1:
        if not j.application.shellconfig.interactive:
            print "Found multiple packages %s" % (packages)
            j.application.stop(1)
        else:
            packages = j.console.askChoiceMultiple(packages, "Multiple packages found. Select:")

    return packages, args

def getProcess(parser=None):
    parser = parser or ArgumentParser()
    parser.add_argument('-d', '--domain', help='Process domain name')
    parser.add_argument('-n', '--name', help='Process name')
    return parser.parse_args()

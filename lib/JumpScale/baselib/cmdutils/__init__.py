from JumpScale import j
import JumpScale.baselib.jpackages #load jpackages
import argparse


def getJPackage(parser=None,installed=None,domain=None):
    if installed:
        domain=""
    parser = parser or argparse.ArgumentParser()
    parser.add_argument('-n','--name',required=False, help='Name of jpackage to be installed')
    parser.add_argument('-d','--domain',required=False, help='Name of jpackage domain to be installed')
    parser.add_argument('-v','--version',required=False, help='Version of jpackage to be installed')

    args = parser.parse_args()

    if args.domain<>None:
        domain=args.domain

    if args.name==None:
        args.name=""
    package = j.packages.find(name=args.name, domain=domain, version=args.version,installed=installed)


    if len(package) == 0:
        if installed:
            print "Could not find package with name '%s' in domain '%s' with version '%s' which is installed." % (args.name, domain, args.version)
        else:
            print "Could not find package with name '%s' in domain '%s' with version '%s'" % (args.name, domain, args.version)
        j.application.stop(1)
    elif len(package) > 1:
        if not j.application.shellconfig.interactive:
            print "Found multiple packages %s" % (package)
            j.application.stop(1)
        else:
            package = j.console.askChoiceMultiple(package, "Multiple packages found. Select:")
    else:
        package = package[0]

    return package, args

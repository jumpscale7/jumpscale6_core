from JumpScale import j
import JumpScale.baselib.jpackages #load jpackages
import argparse


def getJPackage(parser=None):
    parser = parser or argparse.ArgumentParser()
    parser.add_argument('-n','--name',required=False, help='Name of jpackage to be installed')
    parser.add_argument('-d','--domain',required=False, help='Name of jpackage domain to be installed')
    parser.add_argument('-v','--version',required=False, help='Version of jpackage to be installed')
    args = parser.parse_args()
    package = j.packages.find(name=args.name, domain=args.domain, verison=args.version)
    if len(package) == 0:
        print "Could not find package with name '%s' in domain '%s' with version '%s'" % (args.name, args.domain, args.version)
        j.application.stop(1)
    elif len(package) > 1:
        if not j.application.shellconfig.interactive:
            print "Found multiple packages %s" % (package)
            j.application.stop(1)
        else:
            package = j.console.askChoice(package, "Multiple packages found. Select one:")
    else:
        package = package[0]

    return package, args

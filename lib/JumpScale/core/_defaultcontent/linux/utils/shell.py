
#@todo fix following new  ways of working (P1)

from optparse import OptionParser
import sys
import os

def main():

    #parse commandline options
    parser = OptionParser()
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='run in debug mode')
    parser.add_option('-n', '--no-default-initialization', dest='init',
            action='store_true', default=False, help='do not perform default JumpScale initialization using JumpScale.InitBase.initialize')
    parser.add_option("-f", "--file", dest="filename", help="Execute file")
    parser.add_option("-c", "--command", dest="command", help="Execute command")
    parser.add_option("-l", "--logserver", dest="logserver", action='store_true', help="Start logserver")
    (options, args) = parser.parse_args()
    
    #execute python file or first argu
    if options.filename or (len(args) > 0 and (args[0].endswith('.py') or args[0].endswith('.pyw'))):
        if options.filename:
            filename = options.filename
        else:
            filename = args[0]
            args = args[1:]
        sys.argv = sys.argv[0:1] + args
        sys.path.append(os.path.dirname(os.path.abspath(filename)))
        exec_ns = {
                '__name__': '__main__',
                'QSHELL_ENV': True,
                }
        execfile(filename, exec_ns)
        sys.exit(0)
    #start logserver
    elif options.logserver:
        try:
            #@todo for backwards compatibility
            from JumpScale.log.LogServer import startlogserver
            startlogserver()
            sys.exit(0)
        except:
            import JumpScale
            from JumpScale.InitBaseCore import q, i
            print "JumpScale logconsole started:"
            q.logger.console.start()
            sys.exit(0)


    #execute command
    elif options.command:
        import JumpScale
        from JumpScale.InitBaseCore import q, i, p
        exec options.command
        sys.exit(0)
    ns = {}
    if not options.init:
        import JumpScale
        from JumpScale.InitBaseCore import q, i

        ns['q'] = q
        ns['i'] = i
        
        q.application.appname = 'qshell'
        q.qshellconfig.interactive=True
        q.application.start()

        # First time Q-Shell is loaded: automatically update list of Q-Packages available on the server.
        mainCfg = q.config.getInifile("main")
        FIRSTRUN_PARAMNAME = "qshell_firstrun"

        #if not mainCfg.checkParam("main", FIRSTRUN_PARAMNAME) or mainCfg.getBooleanValue("main", FIRSTRUN_PARAMNAME) == True:
        #    q.action.start('Retrieving JPackage information from '
        #                   'package servers')
        #    i.jpackages.updateJPackageList()
        #    q.action.stop()
        #    mainCfg.setParam("main", FIRSTRUN_PARAMNAME, False)
        #    mainCfg.write()

        q.qshellconfig.interactive=True
        if options.debug:
            q.logger.consoleloglevel=8
        else:
            q.logger.consoleloglevel=2

        # Run JPackage configure tasklets if any registered
        #from JumpScale.jpackages.client.JPackageConfigure import JPackageConfigure
        #jpackageconfigure = JPackageConfigure()
        #jpackageconfigure.reconfigure()


        # Run JPackage4 configure tasklets if needed
        q.qp._runPendingReconfigeFiles()
        sys.path.append(q.system.fs.joinPaths(q.dirs.baseDir, 'var', 'tests'))
        from JumpScale.Shell import Shell
        
        # Cannot use ipshell or ipshellDebug because I want to twiddle with the namespace as well...
        Shell(debug=options.debug, ns=ns)()

        q.application.stop()

    else:
        # Give pure ipython Shell
        from IPython.Shell import IPShellEmbed
        IPShellEmbed(argv=[], banner="Welcome to IPython", exit_msg="Bye")()

if __name__ == '__main__':
    main()

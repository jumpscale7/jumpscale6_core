from JumpScale import j
import JumpScale.baselib.circus

class CloudBroker(object):

    def startInScreen(self):
        j.tools.circus.manager.stopProcess('cloudbroker')

        for item in ['byobu', 'screen']:
            cmd = 'killall %s' % item
            j.system.process.execute(cmd, dieOnNonZeroExitCode=False)

        j.system.platform.screen.createSession('cloudbroker', ['appserver',])

        print 'Starting cloudbroker appserver...'
        path = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'cloudbroker')
        cmd = 'cd %s; python start_appserver.py' % path
        j.system.platform.screen.executeInScreen('cloudbroker', 'appserver', cmd, wait=1)
        if not j.system.net.waitConnectionTest('localhost', 9999, 30):
            raise RuntimeError('Failed to start appserver')
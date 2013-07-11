from OpenWizzy import o

class ManagerBase(object):

    _servicename = None

    def __init__(self):
        if not self._servicename:
            o.errorconditionhandler.raiseBug("Class ManagerBase must be extended to be used", "Error")

        self._serviceinit = o.system.fs.joinPaths('/', 'etc', 'init.d', self._servicename)
        if not o.system.fs.exists(self._serviceinit):
            o.errorconditionhandler.raiseBug("'%s' init script doesn't exist" % self._servicename, "Error")

    def start(self):
        self._executeCommand('%s %s' % (self._serviceinit, 'start'))
        o.console.echo("'%s' started successfully" % self._servicename)

    def stop(self):
        self._executeCommand('%s %s' % (self._serviceinit, 'stop'))
        o.console.echo("'%s' stopped successfully" % self._servicename)

    def restart(self):
        self._executeCommand('%s %s' % (self._serviceinit, 'restart'))
        o.console.echo("'%s' restarted successfully"  % self._servicename)

    def _executeCommand(self, command):
        o.system.process.execute(command)
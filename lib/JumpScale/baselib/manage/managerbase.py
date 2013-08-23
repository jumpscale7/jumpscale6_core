from JumpScale import j
import os

class ManagerBase(object):

    _servicename = None

    def __init__(self):
        if not self._servicename:
            j.errorconditionhandler.raiseBug("Class ManagerBase must be extended to be used", "Error")
        self._serviceinit = os.path.join('/', 'etc', 'init.d', self._servicename)
        if not os.path.exists(self._serviceinit):
            j.errorconditionhandler.raiseBug("'%s' init script doesn't exist" % self._servicename, "Error")

    def start(self):
        self._executeCommand('%s %s' % (self._serviceinit, 'start'))
        j.console.echo("'%s' started successfully" % self._servicename)

    def stop(self):
        self._executeCommand('%s %s' % (self._serviceinit, 'stop'))
        j.console.echo("'%s' stopped successfully" % self._servicename)

    def restart(self):
        self._executeCommand('%s %s' % (self._serviceinit, 'restart'))
        j.console.echo("'%s' restarted successfully"  % self._servicename)

    def _executeCommand(self, command):
        j.system.process.execute(command)
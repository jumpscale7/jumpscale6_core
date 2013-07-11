import sys

from OpenWizzy import o


def _doNothing(*args, **kwargs):
    '''This function does nothing, used for monkey patching.'''
    pass


class LoggerPatch(object):
    '''
    This logger patch extension changes the log behaviour of Qshell. This is
    done by monkey patching the logger which makes it forward all logging to
    a message server. Note that this patch is automatically applied when the
    extension is loaded. However, it will not if the necessary message server
    isn't available or not running.
    '''

    DEFAULT_ADDRESS = '127.0.0.1:7777'
    CONFIG_PATH = o.system.fs.joinPaths(o.dirs.cfgDir, 'logger_patch.cfg')

    def __init__(self):
        # TODO: Complete documentation.

        self._messageServerClient = None
        self._applied = False
        self.apply()

    def apply(self, *args, **kwargs):
        # TODO: Complete documentation.

        if self._applied:
            print('Logger patch already applied')
            return

        if not hasattr(o.application, 'whoAmIBytestr') or not o.application.whoAmIBytestr:
            o.application.whoAmIBytestr = 12 * '0'  # The whoAmIBytestr should be at least 12 bytes.

        if not o.system.fs.exists(self.CONFIG_PATH):
            print('Logger patch not applied, config not available')
            return

        config = o.tools.inifile.open(self.CONFIG_PATH)

        if not config.checkSection('main')\
            or not config.checkParam('main', 'address'):
            print('Logger patch not applied, config invalid')
            return

        address = config.getValue('main', 'address')

        self._messageServerClient = o.clients.messageserver.get(address)

        # Check if the message server is running by pinging it.
        serverIsRunning = self._messageServerClient.ping()

        if not serverIsRunning:
            print('Logger patch not applied, server not running')
            return

        self._restoreStandardOutAndError()
        self._monkeyPatchLogger()

        self._applied = True

    def configure(self, address=DEFAULT_ADDRESS):
        # TODO: Complete documentation.

        if o.system.fs.exists(self.CONFIG_PATH):
            config = o.tools.inifile.open(self.CONFIG_PATH)
        else:
            config = o.tools.inifile.new(self.CONFIG_PATH)

        if not config.checkSection('main'):
            config.addSection('main')

        config.setParam('main', 'address', address)

    @property
    def isApplied(self):
        # TODO: Complete documentation.

        return self._applied

    def _log(self, message, level=5, tags='', dontprint=False, category=''):
        '''Logs a message by sending it to the message server.'''
        # TODO: Complete documentation.

        if o.logger.nolog or not isinstance(message, str):
            return

        if level <= o.logger.consoleloglevel and not dontprint\
            and o.application.shellconfig.interactive:
            print(message)

        if level <= o.logger.maxlevel:
            logMessage = ','.join([str(level), category, message])
            packedData = o.core.messagehandler.packMessage(
                o.enumerators.MessageServerMessageType.LOG.level, logMessage)

            self._messageServerClient.send(packedData)

    def _monkeyPatchLogger(self):
        '''Monkey patches the qshell logger.'''

        o.logger.cleanup = _doNothing
        o.logger.cleanupLogsOnFilesystem = _doNothing
        o.logger.clear = _doNothing
        o.logger.close = _doNothing
        o.logger.decodeLogMessage = _doNothing
        o.logger.exception = _doNothing
        o.logger.log = self._log
        o.logger.logs = []
        o.logger.logTargetAdd = _doNothing
        o.logger.logTargets = []
        o.logger.nolog = False

    def _restoreStandardOutAndError(self):
        '''Restores the standard out and standard error.'''

        if hasattr(sys, '_stdout_ori'):
            sys.stdout = sys._stdout_ori

        if hasattr(sys, '_stderr_ori'):
            sys.stderr = sys._stderr_ori
        else:
            sys.stderr = sys.stdout

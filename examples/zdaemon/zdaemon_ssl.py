
from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("zdaemon")

j.logger.consoleloglevel = 6

# if sslkeyvaluestor==None then means local FS will be used
zd = j.core.zdaemon.getZDaemon(port=5555, nrCmdGreenlets=50, sslorg="myorg", ssluser="servertest", sslkeyvaluestor=None)

ZDaemonCMDS = j.core.zdaemon.getZDaemonCMDS()  # get base class which needs to be used as basis for commands


class MyCommands(ZDaemonCMDS):

    def __init__(self, daemon):
        self.daemon = daemon

    def authenticate(self, session):
        return True  # will authenticall all (is std)

    def pingcmd(self, session):
        return "pong"

    def echo(self, msg, session):
        return msg

zd.addCMDsInterface(MyCommands)  # pass as class not as object !!!
zd.start()

j.application.stop()

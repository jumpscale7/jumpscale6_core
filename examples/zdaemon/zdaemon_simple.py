
from JumpScale import j


import JumpScale.grid.zdaemon

j.application.start("zdaemon")

j.logger.consoleloglevel = 6

zd = j.core.zdaemon.getZDaemon(port=3333, nrCmdGreenlets=50)


class MyCommands():

    def __init__(self, daemon):
        self.daemon = daemon

    def authenticate(self, user, login, **args):
        return True  # will authenticall all (is std)

    def pingcmd(self, **args):
        return "pong"

    def echo(self, msg="", **args):
        return msg

zd.addCMDsInterface(MyCommands,"acategory")  # pass as class not as object !!!
zd.start()

j.application.stop()

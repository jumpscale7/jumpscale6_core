import os
import struct

from JumpScale import j

j.application.start("pexpect")

import JumpScale.baselib.expect


e=j.tools.expect.new("sh")

do=e.execShellCmd

do("cd /etc")
print do("ls")


# from IPython import embed
# print "DEBUG NOW main"
# embed()


j.application.stop()

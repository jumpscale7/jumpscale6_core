# import pybloom
import struct

from JumpScale import j

j.application.start("rsa")


import JumpScale.baselib.ssl

# j.tools.ssl.createKeyPair()
ssl = j.tools.ssl.getSSLHandler()
ssl.test()

ssl.perftest()

j.application.stop()

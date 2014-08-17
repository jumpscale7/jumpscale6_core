import os
import struct

from JumpScale import j

import JumpScale.baselib.serializers

j.application.start("blowfishtest")

from random import randrange

msg = ""
for i in range(1000):
    msg += chr(randrange(0, 256))

key = ""
for i in range(56):
    key += chr(randrange(0, 256))


# b means blowfish
s = j.db.serializers.getSerializerType("b", key=key)

nr = 100000
j.base.timer.start()
for i in range(nr):
    data = s.dumps(msg)

j.base.timer.stop(nr)


j.application.stop()

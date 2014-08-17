import os
import struct

from JumpScale import j

import JumpScale.baselib.serializers

j.application.start("blowfishtest")

from random import randrange

msg = ""
for i in range(500):
    msg += chr(randrange(0, 256))

key = ""
for i in range(56):
    key += chr(randrange(0, 256))

serializationstr = "mcb"
s = j.db.serializers.get(serializationstr, key=key)
print s.loads(s.dumps("some data"))


def perftest(data):
    nr = 10000
    j.base.timer.start()
    for i in range(nr):
        data1 = s.dumps(data)
        data2 = s.loads(data1)

    j.base.timer.stop(nr)

serializationstr = "mcb"
s = j.db.serializers.get(serializationstr, key=key)
perftest(data=msg)

j.application.stop()

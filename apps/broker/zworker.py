#
##  Paranoid Pirate worker
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof@incubaid.com
#
from pylabs.InitBase import *
import os
import time
import sys 
from random import randint
import time
import ujson
import zmq

q.application.appname = "zworker"
q.application.start()

q.core.grid.init()

q.logger.log("test message2", level=5, category="a.cat")

q.errorconditionhandler.raiseBug(message="a test bug",category="my.cat.2")

q.application.stop()


if len(sys.argv)==5:
    addr=sys.argv[1] 
    port=int(sys.argv[2])
    instance=int(sys.argv[3])
    roles=sys.argv[4].split(",")
elif len(sys.argv)==1:
    addr="localhost"
    port=5556
    instance=1
    roles=["system.1","*"]
else:
    raise RuntimeError("Format needs to be: 'python zworker.py 127.0.0.1 5556 4'")

q.core.grid.startZWorker(addr=addr,port=port,instance=instance,roles=roles)

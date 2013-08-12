#
##  Paranoid Pirate worker
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof@incubaid.com
#
from OpenWizzy import o
import OpenWizzy.grid
import sys 

o.application.appname = "zworker"
o.application.start()

o.logger.consoleloglevel=3

o.core.grid.init()

o.logger.consoleloglevel=1

# nr=1000
# o.base.timer.start()
# for i in range(nr):
#     o.logger.log("test %s"%i)

# o.base.timer.stop(nr)


if len(sys.argv)==5:
    addr=sys.argv[1] 
    port=int(sys.argv[2])
    instance=int(sys.argv[3])
    if sys.argv[4].find(",")==-1:
    	roles=[sys.argv[4]]
    else:
    	roles=sys.argv[4].split(",")
elif len(sys.argv)==1:
    addr="localhost"
    port=5556
    instance=1
    roles=["*"]
else:
    raise RuntimeError("Format needs to be: 'python zworker.py 127.0.0.1 5556 4 roles1,roles2,roles.sub.1,system'")

o.core.grid.startZWorker(addr=addr,port=port,instance=instance,roles=roles)

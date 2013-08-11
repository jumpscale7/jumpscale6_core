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

o.core.grid.init()

if len(sys.argv)==4:
    addr=sys.argv[1] 
    port=int(sys.argv[2])
    instance=int(sys.argv[3])
elif len(sys.argv)==1:
    addr="localhost"
    port=5556
    instance=1
else:
    raise RuntimeError("Format needs to be: 'python zworker.py 127.0.0.1 5556 4'")

o.core.grid.startZWorker(addr=addr,port=port,instance=instance)

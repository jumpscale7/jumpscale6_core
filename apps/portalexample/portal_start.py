# this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
# monkey.patch_all()
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_thread()
monkey.patch_time()

import time
import os
import subprocess
from JumpScale import j
import JumpScale.portal

import sys

if __name__ == '__main__':
     
    if 'PORTAL_MAIN' in os.environ:
        args=sys.argv
        instance=args[1]
    
        jp = j.packages.findNewest('jumpscale', 'portal')
        jp = jp.load(instance=instance)
        j.application.instanceconfig = jp.hrd_instance
    
        j.application.start("portal")
    
        server=j.core.portal.getServer()
        server.start()
        j.application.stop()
    else:
        while True:
            env = os.environ.copy()
            env['PORTAL_MAIN'] = 'true'
            print('Loading portal')
            exitcode = subprocess.call([sys.executable] + sys.argv, env=env)
            if exitcode != 3:
                 j.application.stop(exitcode)

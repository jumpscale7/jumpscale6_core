#this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
# monkey.patch_all()
monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()
import time
from JumpScale import j
import JumpScale.portal
from JumpScale.baselib.cmdutils import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--instance', help="Gridportal instance", required=True)

opts = parser.parse_args()

jp = j.packages.findNewest('jumpscale', 'portal')
jp = jp.load(instance=opts.instance)
j.application.instanceconfig = jp.hrd_instance

j.application.start("jumpscale:gridportal")
j.application.initGrid()

j.logger.disable()

j.core.portal.getServer().start()


j.application.stop()

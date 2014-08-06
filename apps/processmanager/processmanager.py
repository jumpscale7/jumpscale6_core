#!/usr/bin/env python
#this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
# gevent.monkey.patch_all()

monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()

from JumpScale import j

import JumpScale.grid.processmanager
from JumpScale.baselib.cmdutils import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--instance', help="Processmanager instance", required=True)
parser.add_argument('--nodeid')
opts = parser.parse_args()
jp = j.packages.findNewest('jumpscale', 'processmanager')
jp = jp.getInstance(opts.instance)
j.application.instanceconfig = jp.hrd_instance

import JumpScale.lib.diskmanager

import JumpScale.baselib.stataggregator

j.application.start("jumpscale:processmanager")

j.logger.consoleloglevel = 5
print 'start init grid'
j.core.grid.init()
print 'start processmanger'
j.core.processmanager.start()

j.application.stop()

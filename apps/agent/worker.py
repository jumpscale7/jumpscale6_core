#!/usr/bin/env python
import sys
from redis import * 
from rq import Queue, Connection, Worker

from JumpScale.baselib import cmdutils
from JumpScale import j
sys.path.insert(0,j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts"))

import psutil

j.system.platform.psutil=psutil

import JumpScale.baselib.graphite

import JumpScale.lib.diskmanager

import JumpScale.baselib.stataggregator

j.application.start("jumpscale:worker")
j.application.initGrid()

parser = cmdutils.ArgumentParser()
parser.add_argument("-wn", '--workername', help='Worker name')
parser.add_argument("-qn", '--queuename', help='Queue name')
parser.add_argument("-pw", '--auth', help='Authentication of redis')
parser.add_argument("-a", '--addr', help='Address of redis')
parser.add_argument("-p", '--port', help='Port of redis')

opts = parser.parse_args()

# Preload libraries


# Provide queue names to listen to as arguments to this script,
# similar to rqworker

if opts.addr==None or opts.port==None:
    raise RuntimeError("Please provide addr & port")


redis = Redis(opts.addr, int(opts.port), password=opts.auth)


qs = Queue(opts.queuename,connection=redis)
w = Worker(qs,name=opts.workername,connection=redis)

def my_handler(job, *exc_info):#exc_type, exc_value, traceback):
    exc_type, exc_value, traceback=exc_info 
    j.errorconditionhandler.sendMessageToSentry(modulename=None,message="Could not execute work on worker. Crash.",\
        ttype="worker.execution.error",tags="",extra={},level="error",tb=traceback)


w.push_exc_handler(my_handler)


w.work()

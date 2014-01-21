#!/usr/bin/env python
import sys
from rq import Queue, Connection, Worker

from JumpScale.baselib import cmdutils

parser = cmdutils.ArgumentParser()
parser.add_argument("-wn", '--workername', help='Worker name')
parser.add_argument("-qn", '--queuename', help='Queue name')
parser.add_argument("-pw", '--auth', help='Authentication of redis')
parser.add_argument("-a", '--addr', help='Address of redis')
parser.add_argument("-p", '--port', help='Port of redis')

opts = parser.parse_args()

# Preload libraries
from JumpScale import j

# Provide queue names to listen to as arguments to this script,
# similar to rqworker

redis = Redis(opts.addr, opts.port, password=opts.auth)

with Connection():

    qs = Queue(opts.queuename)
    w = Worker(qs,name=opts.workername)
    w.work()

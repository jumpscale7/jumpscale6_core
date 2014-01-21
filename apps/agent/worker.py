#!/usr/bin/env python
import sys
from redis import * 
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

if opts.addr==None or opts.port==None:
    raise RuntimeError("Please provide addr & port")


redis = Redis(opts.addr, int(opts.port), password=opts.auth)


qs = Queue(opts.queuename,connection=redis)
w = Worker(qs,name=opts.workername,connection=redis)

from raven import Client
from rq.contrib.sentry import register_sentry
client = Client('http://18275531e40849ae8f259a4edd8f1c22:d43b0396addb4b789cd6c325a9ceb36e@localhost:9000/2')
# register_sentry(client, w)
client.name="kds"

def my_handler(job, *exc_info):#exc_type, exc_value, traceback):
    client.captureException(
        exc_info=exc_info,
        extra={
            'job_id': job.id,
            'func': job.func_name,
            'args': job.args,
            'kwargs': job.kwargs,
            'description': job.description,
            })    

w.push_exc_handler(my_handler)


w.work()

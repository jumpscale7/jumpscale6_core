from JumpScale import j
import time
import JumpScale.baselib.redis

descr = """
Gather node's healthchecks
"""

organization = "jumpscale"
name = 'healthchecker_gathering'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "gather.healthchecker"

period = 1 #always in sec
enable = True
async = False
roles = ["*"]


def action():
    redisclient = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    checks = ['processmanager', 'redis', 'disks', 'workers']
    result = dict()
    for check in checks:
        if redisclient.exists("healthcheck:%s" % check):
            result[check] = redisclient.get("healthcheck:%s" % check)
    if redisclient.exists("healthcheck:time"):
        result['time'] = redisclient.get("healthcheck:time")
    else:
        result['time'] = time.time()
    return result
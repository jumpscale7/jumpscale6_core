from JumpScale import j
import time
import JumpScale.baselib.redis

descr = """
Gather node's healthchecks (used in macro in portal)
"""

organization = "jumpscale"
name = 'healthchecker_gathering'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "gather.healthchecker"

period = 0 #always in sec
enable = False
async = False
roles = ["*"]


def action():
    redisclient = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    checks = ['processmanager', 'redis', 'disks', 'workers']
    result = dict()
    for check in checks:
        if redisclient.exists("healthcheck:%s" % check):
            result[check] = redisclient.hget("healthcheck:status",check) #should return True or false
            result[check] = redisclient.hget("healthcheck:lastcheck",check) #should return time
    return result
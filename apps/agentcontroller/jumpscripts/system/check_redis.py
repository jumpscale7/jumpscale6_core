from JumpScale import j

descr = """
Checks Redis server status
"""

organization = "jumpscale"
name = 'check_redis'
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.redisstatus"

async = True
roles = ["*"]


def action():
    import JumpScale.baselib.redis
    ports = (7767, 7768, 7769)
    result = dict()
    for port in ports:
        pids = j.system.process.getPidsByPort(port)
        if not pids:
            continue
        rproc = j.system.process.getProcessObject(pids[0])
        rcl = j.clients.redis.getRedisClient('127.0.0.1', port)
        result[port] = {'alive': rcl.ping(), 'memory_usage': '%s MB' % '{:.2f}'.format(rproc.get_memory_info()[0]/1024.0/1024.0)}

    return result
    


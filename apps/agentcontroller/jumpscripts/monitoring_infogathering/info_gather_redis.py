from JumpScale import j

descr = """
Checks Redis server status
"""

organization = "jumpscale"
name = 'info_gather_redis'
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.redisstatus"

async = False
roles = ["*"]

period=0

log=False

def action():
    import JumpScale.baselib.redis
    ports = [7768, 7766, 7767]
    masterip = j.application.config.get('grid.master.ip')
    if j.system.net.isIpLocal(masterip):
        ports.append(7769)
    result = dict()
    for port in ports:
        pids = j.system.process.getPidsByPort(port)
        if not pids:
            result[port] = {'state': 'HALTED', 'memory_usage': 0}
        else:
            rproc = j.system.process.getProcessObject(pids[0])
            rcl = j.clients.redis.getRedisClient('127.0.0.1', port)
            state = 'RUNNING' if rcl.ping() else 'BROKEN'
            result[port] = {'state': state, 'memory_usage': rproc.get_memory_info()[0]}

    return result

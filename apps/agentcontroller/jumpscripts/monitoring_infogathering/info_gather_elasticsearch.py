from JumpScale import j

descr = """
Checks ElasticSearch status
"""

organization = "jumpscale"
name = 'info_gather_elasticsearch'
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.esstatus"

async = False
roles = ["*"]
enable = True
period=0

def action():
    import JumpScale.baselib.elasticsearch
    escl = j.clients.elasticsearch.get()
    health = escl.health()

    size = 0
    indices = escl.status()['indices']
    for index, data in indices.iteritems():
        size += data['index']['size_in_bytes']

    pid = j.system.process.getPidsByPort(9200)[0]
    process = j.system.process.getProcessObject(pid)
    memoryusage, _ = process.get_memory_info()

    return {'size': size, 'health': health, 'memory_usage': memoryusage}


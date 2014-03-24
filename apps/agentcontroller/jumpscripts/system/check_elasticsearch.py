from JumpScale import j

descr = """
Checks ElasticSearch status
"""

organization = "jumpscale"
name = 'check_elasticsearch'
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.esstatus"

async = True
roles = ["*"]


def action():
    import JumpScale.baselib.elasticsearch
    escl = j.clients.elasticsearch.get()
    health = escl.health()

    hrd = j.core.hrd.getHRD(j.system.fs.joinPaths(j.dirs.cfgDir, 'startup', 'jumpscale__elasticsearch.hrd'))
    path = hrd.get('process.args').rsplit('es.config=')[1]
    configdata = j.system.fs.fileGetUncommentedContents(path)
    configs = dict()
    for config in configdata:
        if ':' in config:
            key, value = config.split(':')
            configs[key.strip()] = value.strip()
    size = j.system.fs.fileSize(configs.get('path.data', '/opt/data/elasticsearch'))

    return {'size': size, 'health': health}


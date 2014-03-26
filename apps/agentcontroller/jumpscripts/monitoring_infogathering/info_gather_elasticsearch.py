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

period=0

def action():
    import JumpScale.baselib.elasticsearch
    escl = j.clients.elasticsearch.get()
    health = escl.health()

    #@todo check memory usage elastic search
    #@todo check index sizes

    return {'size': size, 'health': health}


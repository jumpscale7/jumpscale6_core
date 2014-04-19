from JumpScale import j
from .cloudbroker import CloudBroker

j.base.loader.makeAvailable(j, 'servers')

j.servers.cloudbroker = CloudBroker()
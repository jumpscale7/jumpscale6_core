from JumpScale import j
from ClusterFactory import ClusterFactory

j.base.loader.makeAvailable(j, 'remote')
j.remote.cluster = ClusterFactory()

from ClusterConfigs import *

j.remote.cluster.config=ClusterConfigs()
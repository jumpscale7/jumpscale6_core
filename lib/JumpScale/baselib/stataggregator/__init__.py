from JumpScale import j
from .StatAggregator import StatAggregator

j.base.loader.makeAvailable(j, 'system')
j.system.stataggregator = StatAggregator()

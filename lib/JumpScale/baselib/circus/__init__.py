from JumpScale import j

from .Circus import Circus

j.base.loader.makeAvailable(j, 'tools')

j.tools.circus=Circus()

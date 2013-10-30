from JumpScale import j

from .CircusCL import CircusCL
from .CircusManager import CircusManager

j.base.loader.makeAvailable(j, 'tools.circus')

j.tools.circus.client = CircusCL()
j.tools.circus.manager = CircusManager()

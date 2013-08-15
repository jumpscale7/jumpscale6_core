from OpenWizzy import o
from .HashTool import HashTool
o.base.loader.makeAvailable(o, 'tools')
o.tools.hash = HashTool()

from OpenWizzy import o
from .CodeTools import CodeTools
from .CodeManager import CodeManager
o.base.loader.makeAvailable(o, '')
o.base.loader.makeAvailable(o, 'codetools')
o.codetools = CodeTools()
o.codetools.codemanager = CodeManager()

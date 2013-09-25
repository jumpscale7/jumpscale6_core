__version__ = '6.0.0'
__all__ = ['__version__', 'j']

import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
del pkgutil



class JumpScale():
	def __init__(self):
		pass

j = JumpScale()
from . import base
from . import core
import baselib.codeexecutor
import baselib.jpackages
import baselib.tags

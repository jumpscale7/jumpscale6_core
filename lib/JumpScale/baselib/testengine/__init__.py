from JumpScale import j
import JumpScale.baselib.params
from .TestEngine import TestEngine

j.base.loader.makeAvailable(j, 'tools')
j.tools.testengine = TestEngine()

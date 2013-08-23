from OpenWizzy import o
import OpenWizzy.baselib.params
from .TaskletEngine import TaskletEngineFactory

o.base.loader.makeAvailable(o, 'core')
o.core.taskletengine = TaskletEngineFactory()

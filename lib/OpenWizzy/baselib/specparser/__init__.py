from OpenWizzy import o
import OpenWizzy.baselib.code
from .SpecParser import SpecParserFactory
o.base.loader.makeAvailable(o, 'core')
o.core.specparser = SpecParserFactory()

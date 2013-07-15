from OpenWizzy import o
from .OSISFactory import OSISFactory
import OpenWizzy.baselib.hrd
import OpenWizzy.baselib.key_value_store
o.base.loader.makeAvailable(o, 'core')
o.core.osis = OSISFactory()

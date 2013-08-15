from OpenWizzy import o
import OpenWizzy.baselib.code
from .OSIS import OSIS
o.base.loader.makeAvailable(o, 'core')
o.core.osismodel = OSIS()


from OpenWizzy import o
from .OSISFactory import OSISFactory
o.base.loader.makeAvailable(o, 'core')
o.core.osis = OSISFactory()

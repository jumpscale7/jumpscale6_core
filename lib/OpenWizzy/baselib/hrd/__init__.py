from OpenWizzy import o
from .HumanReadableData import HumanReadableDataFactory
o.base.loader.makeAvailable(o, 'core')
o.core.hrd = HumanReadableDataFactory()

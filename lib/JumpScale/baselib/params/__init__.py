from OpenWizzy import o
from .Params import ParamsFactory
o.base.loader.makeAvailable(o, 'core')

o.core.params = ParamsFactory()


__all__ = ['Time','IDgenerator', ]

from OpenWizzy import o

from OpenWizzy.core.base.time.Time import Time
from OpenWizzy.core.base.idgenerator.IDGenerator import IDGenerator

class Empty():
    pass

if not o.__dict__.has_key("base"):
    o.base=Empty()

    
o.base.time=Time()
o.base.idgenerator=IDGenerator()
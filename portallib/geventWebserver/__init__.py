from OpenWizzy import o
from .GeventWebserver import GeventWebserverFactory
o.base.loader.makeAvailable(o, 'web')
o.web.geventws = GeventWebserverFactory()

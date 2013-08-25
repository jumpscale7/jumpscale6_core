from JumpScale import j
from .GeventWebserver import GeventWebserverFactory
j.base.loader.makeAvailable(j, 'web')
j.web.geventws = GeventWebserverFactory()

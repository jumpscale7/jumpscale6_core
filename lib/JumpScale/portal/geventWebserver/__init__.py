from JumpScale import j
from .GeventWebserverFactory import GeventWebserverFactory
j.base.loader.makeAvailable(j, 'web')
j.web.geventws = GeventWebserverFactory()

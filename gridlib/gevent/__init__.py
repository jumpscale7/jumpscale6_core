from OpenWizzy import o
from .GeventLoopFactory import GeventLoopFactory
o.base.loader.makeAvailable(o, 'core')
o.core.gevent = GeventLoopFactory()

from OpenWizzy import o
from .HgLibFactory import HgLibFactory
o.base.loader.makeAvailable(o, 'clients')
o.clients.mercurial = HgLibFactory()

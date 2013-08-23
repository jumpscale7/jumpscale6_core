from OpenWizzy import o

from .BlobStor import BlobStorFactory
import OpenWizzy.baselib.hash

o.base.loader.makeAvailable(o, 'clients')

o.clients.blobstor=BlobStorFactory()

from OpenWizzy import o
from .HttpClient import HttpClient
o.base.loader.makeAvailable(o, 'clients')
o.clients.http = HttpClient()

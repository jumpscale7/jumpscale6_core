from OpenWizzy import o
from HgLibFactory import HgLibFactory

class Empty():
	pass

if not  o.__dict__.has_key("clients"):
    o.clients=Empty()

o.clients.mercurial=HgLibFactory()



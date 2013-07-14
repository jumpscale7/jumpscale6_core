from OpenWizzy import o
from LRUCache import LRUCacheFactory

class Empty():
	pass

if not  o.__dict__.has_key("db"):
    o.db=Empty()

o.db.cache=LRUCacheFactory()



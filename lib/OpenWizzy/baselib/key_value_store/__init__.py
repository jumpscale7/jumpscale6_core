from OpenWizzy import o
from store_factory import KeyValueStoreFactory

class Empty():
    pass

if not o.__dict__.has_key("db"):
    o.db=Empty()

o.db.keyvaluestore=KeyValueStoreFactory()
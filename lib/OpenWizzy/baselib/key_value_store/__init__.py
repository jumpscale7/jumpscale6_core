from OpenWizzy import o
from .store_factory import KeyValueStoreFactory
o.base.loader.makeAvailable(o, 'db')
o.db.keyvaluestore = KeyValueStoreFactory()

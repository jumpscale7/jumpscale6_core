from beaker.container import NamespaceManager
class OsisBeaker(NamespaceManager):
    def __init__(self, id, namespace_args, **kwargs):
        self._namespace = 'system'
        self._category = 'sessioncache'
        self.namespace = id
        self._client = namespace_args['client']

    def __getitem__(self, key):
        key = "%s_%s" % (self.namespace, key)
        try:
            return self._client.get(categoryname=self._category, namespace=self._namespace, key=key)
        except:
            raise KeyError(key)

    def __setitem__(self, key, value):
        nkey = "%s_%s" % (self.namespace, key)
        if 'user' not in value:
            self._remove(key)
            return
        elif value['user'] == 'guest':
            return
        self._client.set(categoryname=self._category, namespace=self._namespace, key=nkey, value=value)

    def _remove(self, key):
        key = "%s_%s" % (self.namespace, key)
        self._client.delete(categoryname=self._category, namespace=self._namespace, key=key)
    def __contains__(self, key):
        key = "%s_%s" % (self.namespace, key)
        return self._client.exists(key)


    def acquire_read_lock(self, **kwargs):
        return True

    def release_read_lock(self, **kwargs):
        return True

    def acquire_write_lock(self, **kwargs):
        return True

    def release_write_lock(self, **kwargs):
        return True

from arakoon_store import ArakoonKeyValueStore
from file_system_store import FileSystemKeyValueStore
from memory_store import MemoryKeyValueStore
from redis_store import RedisKeyValueStore
from OpenWizzy import o


class KeyValueStoreFactory(object):
    '''
    The key value store factory provides logic to retrieve store instances. It
    also caches the stores based on their type, name and namespace.
    '''

    def __init__(self):
        self._cache = dict()

    def getArakoonStore(self, namespace='',serializers=[o.db.serializers.pickle]):
        '''
        Gets an Arakoon key value store.

        @param namespace: namespace of the store, defaults to None
        @type namespace: String

        @param defaultPymodelSerializer: default Pymodel serializer
        @type defaultPymodelSerializer: Object

        @return: key value store
        @rtype: ArakoonKeyValueStore
        '''
        key = '%s_%s' % ("arakoon", namespace)
        if key not in self._cache:
            if namespace=="":
                namespace="main"
            self._cache[key] = ArakoonKeyValueStore(namespace,serializers=serializers)
        return self._cache[key]

    def getFileSystemStore(self, namespace='', baseDir=None,serializers=[o.db.serializers.pickle]):
        '''
        Gets a file system key value store.

        @param namespace: namespace of the store, defaults to an empty string
        @type namespace: String

        @param baseDir: base directory of the store, defaults to o.dirs.db
        @type namespace: String

        @param defaultPymodelSerializer: default Pymodel serializer
        @type defaultPymodelSerializer: Object

        @return: key value store
        @rtype: FileSystemKeyValueStore
        '''

        key = '%s_%s' % ("fs", namespace)
        if key not in self._cache:
            if namespace=="":
                namespace="main"
            self._cache[key] = FileSystemKeyValueStore(namespace, baseDir=baseDir,serializers=serializers)
        return self._cache[key]

    def getMemoryStore(self):
        '''
        Gets a memory key value store.

        @return: key value store
        @rtype: MemoryKeyValueStore
        '''
        return MemoryKeyValueStore()

    def getRedisStore(self, namespace='',host='localhost',port=6379,db=0,key='',serializers=None):
        '''
        Gets a memory key value store.

        @param name: name of the store
        @type name: String

        @param namespace: namespace of the store, defaults to None
        @type namespace: String

        @return: key value store
        @rtype: MemoryKeyValueStore
        '''
        key = '%s_%s_%s' % ("redis", port, namespace)
        if key not in self._cache:
            self._cache[key] = RedisKeyValueStore(namespace=namespace,host=host,port=port,db=db,key=key,serializers=serializers)
        return self._cache[key]


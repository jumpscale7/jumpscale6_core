import ujson
from JumpScale import j
blocksize = 20*1024*1024

def _read_file(path, block_size=0):
    with open(path, 'rb') as f:
        while True:
            piece = f.read(block_size)
            if piece:
                yield piece
            else:
                return

def _dump2stor(store, bucketname, data):
        if len(data)==0:
            return ""       
        key = j.tools.hash.md5_string(data)
        if not key in store.list_objects(bucketname):
            store.set_object(bucketname, key, data)
        return key

def store_metadata(store, mdbucketname, backupname, backupmetadata):
    pools = store.list_pools()
    if not mdbucketname in pools:
        store.create_pool(mdbucketname)
    store.set_object(mdbucketname, backupname, ujson.dumps(backupmetadata))

def backup(store, bucketname, f):
    hashes = []
    pools = store.list_pools()
    if not bucketname in pools:
        store.create_pool(bucketname)
    for data in _read_file(f, blocksize):
        hashes.append(_dump2stor(store, bucketname, data))
    return {'path':f, 'fileparts':hashes}



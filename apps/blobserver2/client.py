import tempfile
import tarfile

from JumpScale import j

import JumpScale.grid.zdaemon
import JumpScale.baselib.blobstor2

j.application.start("jumpscale:blobserver2test")

j.logger.consoleloglevel = 5

passwd = j.application.config.get('grid.master.superadminpasswd')
login="root"

namespace="test"

client = j.clients.blobstor2.getClient(namespace,login=login, passwd=passwd)
client2 = j.clients.blobstor2.getClient(namespace, port=2346, login=login, passwd=passwd)

blob=""
for i in range(1024*1024*4):
    blob+="A"
#4MB

hash = j.tools.hash.md5_string(blob)

blob2 = "EXISTS IN PARENT BLOB"
hash2 = j.tools.hash.md5_string(blob2)
client2.set(hash2, blob2, repoId="repo1")

client.deleteNamespace()

print "start"

blob_missing = client.get(hash2)
print "CHECKING MISSING BLOB"
assert blob_missing == blob2 , "MISSING BLOB CANNOT BE FOUND"

print "SUCCESS"

client.set(hash, blob, repoId="repo1")
client.set(hash, blob, repoId="repo2")

blob2 = client.get(hash)

assert blob2==blob

md = client.getMD(hash)
print md

blob2 = client.delete(hash, repoId="repo1")

md = client.getMD(hash)
print md

assert client.exists(hash, repoId="repo2")==True
assert client.exists(hash, repoId="repo1")==False
assert client.exists(hash)==True

blob2 = client.delete(hash, repoId="repo2")
assert client.exists(hash)==False

# TESTING Blob Patches

print "TESTING BLOB PATCH"
client.deleteNamespace()

blob = "THIS IS A BLOB"
hash = j.tools.hash.md5_string(blob)

# Set the Blob
client.set(hash, blob)

keyList = [hash]
blob_tar = client.getBlobPatch(keyList)

blob_patch = tempfile.mktemp(prefix="blob_", suffix=".tar")
j.system.fs.writeFile(blob_patch, blob_tar)

blob_target = tempfile.mkdtemp(prefix="blobtarget_")
tar = tarfile.open(blob_patch)
tar.extractall(path=blob_target)
tar.close()

print "DONE!"

j.application.stop()


from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("jumpscale:blobserver2test")

j.logger.consoleloglevel = 5

passwd = j.application.config.get('grid.master.superadminpasswd')
login="root"

client= j.servers.zdaemon.getZDaemonClient("127.0.0.1",port=2345,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobserver")
client2= j.servers.zdaemon.getZDaemonClient("127.0.0.1",port=2346,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobserver")

blob=""
for i in range(1024*1024*4):
    blob+="A"
#4MB

hash=j.tools.hash.md5_string(blob)
namespace="test"

blob2 = "EXISTS IN PARENT BLOB"
hash2 = j.tools.hash.md5_string(blob2)
client2.set(namespace, hash2, blob2, repoId="repo1")

client.deleteNamespace("test")

print "start"

blob_missing = client.get(namespace, hash2)
print "CHECKING MISSING BLOB"
assert blob_missing == blob2 , "MISSING BLOB CANNOT BE FOUND"

print "SUCCESS"

client.set(namespace, hash, blob, repoId="repo1")
client.set(namespace, hash, blob, repoId="repo2")

blob2 = client.get(namespace, hash)

assert blob2==blob

md = client.getMD(namespace, hash)
print md

blob2 = client.delete(namespace, hash, repoId="repo1")

md = client.getMD(namespace, hash)
print md

assert client.exists(namespace, hash, repoId="repo2")==True
assert client.exists(namespace, hash, repoId="repo1")==False
assert client.exists(namespace, hash)==True

blob2 = client.delete(hash, namespace, repoId="repo2")
assert client.exists(hash, namespace)==False


j.application.stop()


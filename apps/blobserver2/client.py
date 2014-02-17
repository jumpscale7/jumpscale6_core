from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("jumpscale:blobserver2test")

j.logger.consoleloglevel = 5

passwd = j.application.config.get('grid.master.superadminpasswd')
login="root"

client= j.servers.zdaemon.getZDaemonClient("127.0.0.1",port=2345,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobserver")

blob=""
for i in range(1024*1024*4):
    blob+="A"
#4MB

hash=j.tools.hash.md5_string(blob)
namespace="test"

client.deleteNamespace("test")

print "start"

client.set(hash,namespace,blob,repoId="repo1") 
client.set(hash,namespace,blob,repoId="repo2")

blob2=client.get(hash,namespace)

assert blob2==blob

md=client.getMD(hash,namespace)
print md

blob2=client.delete(hash,namespace,repoId="repo1")

md=client.getMD(hash,namespace)
print md

assert client.exists(hash,namespace,repoId="repo2")==True
assert client.exists(hash,namespace,repoId="repo1")==False
assert client.exists(hash,namespace)==True

blob2=client.delete(hash,namespace,repoId="repo2")
assert client.exists(hash,namespace)==False


j.application.stop()


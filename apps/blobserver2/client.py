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

print "start"
client.set(hash,blob) 
blob2=client.get(hash) 

assert blob2==blob

assert client.exists(hash)==True 

j.application.stop()


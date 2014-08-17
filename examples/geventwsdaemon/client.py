from JumpScale import j
import JumpScale.grid.geventws
cl = j.servers.geventws.getClient('localhost', 8888, 'example')
print cl.ping()

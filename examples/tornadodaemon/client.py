from JumpScale import j
import JumpScale.grid.tornado
cl = j.servers.tornado.getClient('localhost', 8888, 'example')
print cl.ping()

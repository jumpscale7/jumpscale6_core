from OpenWizzy import o
import OpenWizzy.grid.tornado
cl = o.servers.tornado.getClient('localhost', 8888, 'example', ssl=True)
print cl.ping()


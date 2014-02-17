from JumpScale import j

j.application.start("jumpscale:agentcontrollertest")

j.logger.consoleloglevel = 5
# import JumpScale.grid.zdaemon
# cl=j.core.zdaemon.getZDaemonClient(addr="localhost", port=5544, category="osis",\
#                 user="root", passwd="rooter",gevent=True)
import JumpScale.grid.agentcontroller
j.clients.agentcontroller.configure("127.0.0.1")

from IPython import embed
print "DEBUG NOW test"
embed()


j.application.stop()


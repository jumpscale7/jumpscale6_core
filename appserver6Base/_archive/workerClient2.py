from pylabs.InitBase import *
import os

q.application.appname = "workerclient"
q.application.start()

cl=q.system.socketserver.getClient("127.0.0.1",4333,"1234")

cl.senddata("test")

print cl.readdata()

q.application.stop()

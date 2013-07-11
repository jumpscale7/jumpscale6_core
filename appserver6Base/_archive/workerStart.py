from pylabs.InitBase import *
import os

q.application.appname = "worker"
q.application.start()

print "* check app server started" #do this by  checking on ftp then we know for sure appserver also ok
if q.system.net.waitConnectionTest("127.0.0.1",21,30)==False:
    msg="could not start the ftpserver, check in corresponding tab in console."
    raise RuntimeError(msg)
print "* run simulation"


ss=q.system.socketserver.get(4333,"1234")

def handler(data):
    print data
    return "hello"

ss.setDataHandler(handler)

ss.start()

q.application.stop()

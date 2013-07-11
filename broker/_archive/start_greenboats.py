from pylabs.InitBase import *    

q.application.appname = "GreenBoats"
q.application.start()

q.qshellconfig.interactive=True

import time

if q.platform.isWindows():
    q.system.windows.killProcessesFromCommandLines([["python","start_appserver"],["python","ftp"]])

    console=q.tools.winconsole.get()
    console.addTab("startGreenBoats","../../apps/greenboats","python start_appserver.py")
    console.addTab("startftpserver","","start_ftpserver.bat")

    #start appserver
    print "* start all required systems"
    console.start()

    print "* check nginx & appserver started"
    if q.system.net.waitConnectionTest("127.0.0.1",80,20)==False or q.system.net.waitConnectionTest("127.0.0.1",9999,20)==False:
        msg="could not start the appserver & nginx, check in corresponding tab in console."
        raise RuntimeError(msg)
    print "* appserver started."

    print "* check ftp server started"
    if q.system.net.waitConnectionTest("127.0.0.1",21,2)==False:
        msg="could not start the ftpserver, check in corresponding tab in console."
        raise RuntimeError(msg)
    print "* SUCCESS: all started ok."

q.application.stop()

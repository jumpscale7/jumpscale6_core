from OpenWizzy import o
import OpenWizzy.grid
import OpenWizzy.baselib.hrd
import OpenWizzy.baselib.screen
o.application.appname = "startworkers"
o.application.start()


o.core.grid.configureNode(gridid=5,name="", roles=["atestmachine.1","all"], brokerip="localhost",brokerport="5554")

o.core.grid.configureBroker(domain='adomain.com', osisip='localhost', osisport=5544, brokerid=1) #give a unique brokerid can also do automatically but will be confusing
   #if we are master then this needs to be configured, if only participant in grid then not

import time

nrworkers=1
nrclients=1
host="localhost"
port=5556
portbroker=5555
nodeid=1
nrtestsperclient=1

if o.system.platformtype.isWindows():
    o.system.windows.killProcessesFromCommandLines([["python","zworker"]])
    o.system.windows.killProcessesFromCommandLines([["python","zclienttest"]])
    o.system.windows.killProcessesFromCommandLines([["python","zbroker"]])

    console=o.tools.winconsole.get()
    console.tabs=[] #remove qshell & console

    console.addTab("console","","")

    #elastic search
    console.addTab("es",o.system.fs.joinPaths(o.dirs.baseDir),"start_elasticsearch.bat")

    console.addTab("osis",o.system.fs.joinPaths(o.dirs.appDir,"osis"),"python osisServerStart.py")

    console.addTab("broker","","python zbrokerStart.py")
    
    for worker in range(1,nrworkers+1):
        console.addTab("w%s"%worker,"","python zworkerStart.py %s %s %s %s"%(host,port,worker,"system.%s,storagenode"%nodeid))

    for client in range(1,nrclients+1):
        cmd="python zclienttest.py %s %s %s %s"%(host,portbroker,client,nrtestsperclient)
        print cmd
        console.addTab("c%s"%client,"",cmd)

    print "* start all required systems"
    console.start()

    print "* SUCCESS: all started ok."
else:
    screens=["console","osis","logger","broker" ]
    for worker in range(1,nrworkers+1):
        screens.append("w%s"%worker)
    for client in range(1,nrclients+1):
        screens.append("c%s"%client)

    o.system.platform.screen.createSession("broker",screens)
    
    # #kill remainders
    # for item in ["byobu","screen"]:
    #     cmd="killall %s"%item
    #     o.system.process.execute(cmd)

    #start elastic search
    cmd="/etc/init.d/elasticsearch start"
    o.system.process.execute(cmd)

    #start osis
    path=o.system.fs.joinPaths(o.dirs.appDir,"osis")
    cmd="cd %s;python osisServerStart.py"%path
    o.system.platform.screen.executeInScreen("broker","osis",cmd,wait=1)

    #start logger
    path=o.system.fs.joinPaths(o.dirs.appDir,"logger")
    cmd="cd %s;python loggerStart.py"%path
    o.system.platform.screen.executeInScreen("broker","logger",cmd,wait=1)

    #start broker
    cmd="python zbrokerStart.py"
    o.system.platform.screen.executeInScreen("broker","broker",cmd,wait=1)

    for worker in range(1,nrworkers+1):
        cmd="python zworkerStart.py %s %s %s %s"%(host,port,worker,"system/%s,*"%nodeid)
        o.system.platform.screen.executeInScreen("broker","w%s"%worker,cmd,wait=1)

    for client in range(1,nrclients+1):
        cmd="python zclienttest.py %s %s %s %s"%(host,portbroker,client,nrtestsperclient)
        o.system.platform.screen.executeInScreen("broker","c%s"%client,cmd,wait=1)

    print "* started all required systems"


#make sure node is registered to grid (once done is not needed any more afterwards)
# o.core.grid.init()
o.application.stop()

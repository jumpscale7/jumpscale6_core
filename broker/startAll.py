from pylabs.InitBase import *    
q.application.appname = "startworkers"
q.application.start()
q.qshellconfig.interactive=True


q.core.grid.configureNode(gridid=5,name="", roles=["atestmachine.1","all"], brokerip="localhost",brokerport="5554")

q.core.grid.configureBroker(domain='adomain.com', osisip='localhost', osisport=5544, brokerid=1) #give a unique brokerid can also do automatically but will be confusing
   #if we are master then this needs to be configured, if only participant in grid then not

import time

nrworkers=1
nrclients=1
host="localhost"
port=5556
portbroker=5555
nodeid=1
nrtestsperclient=1

if q.platform.isWindows():
    q.system.windows.killProcessesFromCommandLines([["python","zworker"]])
    q.system.windows.killProcessesFromCommandLines([["python","zclienttest"]])
    q.system.windows.killProcessesFromCommandLines([["python","zbroker"]])

    console=q.tools.winconsole.get()
    console.tabs=[] #remove qshell & console

    console.addTab("console","","")

    #elastic search
    console.addTab("es",q.system.fs.joinPaths(q.dirs.baseDir),"start_elasticsearch.bat")

    console.addTab("osis",q.system.fs.joinPaths(q.dirs.appDir,"osis"),"python osisServerStart.py")

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

    q.platform.screen.createSession("broker",screens)
    
    # #kill remainders
    # for item in ["byobu","screen"]:
    #     cmd="killall %s"%item
    #     q.system.process.execute(cmd)

    #start elastic search
    cmd="/etc/init.d/elasticsearch start"
    q.system.process.execute(cmd)

    #start osis
    path=q.system.fs.joinPaths(q.dirs.appDir,"osis")
    cmd="cd %s;python osisServerStart.py"%path
    q.platform.screen.executeInScreen("broker","osis",cmd,wait=1)

    #start logger
    path=q.system.fs.joinPaths(q.dirs.appDir,"logger")
    cmd="cd %s;python loggerStart.py"%path
    q.platform.screen.executeInScreen("broker","logger",cmd,wait=1)

    #start broker
    cmd="python zbrokerStart.py"
    q.platform.screen.executeInScreen("broker","broker",cmd,wait=1)

    for worker in range(1,nrworkers+1):
        cmd="python zworkerStart.py %s %s %s %s"%(host,port,worker,"system/%s,*"%nodeid)
        q.platform.screen.executeInScreen("broker","w%s"%worker,cmd,wait=1)

    for client in range(1,nrclients+1):
        cmd="python zclienttest.py %s %s %s %s"%(host,portbroker,client,nrtestsperclient)
        q.platform.screen.executeInScreen("broker","c%s"%client,cmd,wait=1)

    print "* started all required systems"


#make sure node is registered to grid (once done is not needed any more afterwards)
# q.core.grid.init()
q.application.stop()

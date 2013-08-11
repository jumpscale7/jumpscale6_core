from OpenWizzy import o
import OpenWizzy.grid
import OpenWizzy.baselib.hrd
import OpenWizzy.baselib.screen
o.application.appname = "startworkers"
o.application.start()

o.dirs.appDir = o.system.fs.joinPaths(o.dirs.baseDir, 'apps')

o.core.grid.configureNode(gridid=5,name="", roles=["atestmachine.1","all"], brokerip="localhost",brokerport="5554")

o.core.grid.configureBroker(domain='adomain.com', osisip='localhost', osisport=5544, brokerid=1) #give a unique brokerid can also do automatically but will be confusing
   #if we are master then this needs to be configured, if only participant in grid then not

o.develtools.startPortalByobu()

#make sure node is registered to grid (once done is not needed any more afterwards)
# o.core.grid.init()
o.application.stop()

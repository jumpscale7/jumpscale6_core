from JumpScale import j
import JumpScale.grid
import JumpScale.baselib.hrd
import JumpScale.baselib.screen

j.application.start("startworkers")

j.dirs.appDir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps')

j.core.grid.configureNode(gridid=5, name="", roles=["atestmachine.1", "all"], brokerip="localhost", brokerport="5651")

j.core.grid.configureBroker(domain='adomain.com', osisip='localhost', osisport=5544, brokerid=1)
                            #give a unique brokerid can also do automatically but will be confusing
   # if we are master then this needs to be configured, if only participant in grid then not

j.develtools.startPortalByobu('portalbase')

# make sure node is registered to grid (once done is not needed any more afterwards)
# j.core.grid.init()
j.application.stop()

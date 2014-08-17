from JumpScale import j
import JumpScale.grid.geventws
from mycmds import MyCommands

serv = j.servers.geventws.getServer(8888)
serv.addCMDsInterface(MyCommands, category='example')
serv.start()

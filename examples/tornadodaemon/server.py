from JumpScale import j
import JumpScale.grid.tornado
from mycmds import MyCommands

serv = j.servers.tornado.getServer(8888)
serv.addCMDsInterface(MyCommands, category='example')
serv.start()

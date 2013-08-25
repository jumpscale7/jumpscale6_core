from JumpScale import j
import JumpScale.grid.grid
import JumpScale.grid.osis

j.application.appname = "logger"
j.application.start()


j.core.grid.startLocalLogger()


j.application.stop()

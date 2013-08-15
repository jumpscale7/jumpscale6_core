from OpenWizzy import o
import OpenWizzy.grid.grid
import OpenWizzy.grid.osis

o.application.appname = "logger"
o.application.start()



o.core.grid.startLocalLogger()


o.application.stop()

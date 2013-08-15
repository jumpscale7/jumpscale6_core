from OpenWizzy import o
import OpenWizzy.grid
import OpenWizzy.grid.osis
o.application.appname = "zbroker"
o.application.start()

o.core.grid.startBroker()

o.application.stop()



from OpenWizzy import o
import OpenWizzy.grid.osis

o.application.appname = "osisserver"
o.application.start()

o.core.osis.startDaemon(overwriteImplementation=False)

o.application.stop()

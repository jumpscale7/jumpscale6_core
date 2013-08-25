from JumpScale import j
import JumpScale.grid.osis

j.application.appname = "osisserver"
j.application.start()

j.core.osis.startDaemon(overwriteImplementation=False)

j.application.stop()

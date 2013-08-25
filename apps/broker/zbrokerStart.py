from JumpScale import j
import JumpScale.grid
import JumpScale.grid.osis
j.application.appname = "zbroker"
j.application.start()

j.core.grid.startBroker()

j.application.stop()

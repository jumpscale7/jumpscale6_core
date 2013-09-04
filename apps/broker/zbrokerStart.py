from JumpScale import j
import JumpScale.grid
import JumpScale.grid.osis

j.application.start("zbroker")

j.core.grid.startBroker()

j.application.stop()

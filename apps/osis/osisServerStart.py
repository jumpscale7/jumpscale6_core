from JumpScale import j
import JumpScale.grid.osis

j.application.start("osisserver")

j.core.osis.startDaemon(overwriteImplementation=False)

j.application.stop()

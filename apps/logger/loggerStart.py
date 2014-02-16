from JumpScale import j
import JumpScale.grid.grid
import JumpScale.grid.osis

j.application.start("logger")

raise RuntimeError("do not use, outdated, now we use redis & processmanager")
# j.core.grid.startLocalLogger()


j.application.stop()

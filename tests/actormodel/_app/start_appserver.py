from JumpScale import j
j.application.start('testapp')
import JumpScale.portal
j.core.portal.getServer().start()
j.application.stop()

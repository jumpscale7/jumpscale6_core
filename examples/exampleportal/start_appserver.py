from JumpScale import j
j.application.start('myapp')

import JumpScale.portal  # load portal libraries
j.core.portal.getServer().start()
j.application.stop()

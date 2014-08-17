from JumpScale import j

import JumpScale.lib.sandboxer

j.application.start("jsexamples:libsandboxer")


j.tools.sandboxer.copyLibsTo("nginx","libs")



j.application.stop()

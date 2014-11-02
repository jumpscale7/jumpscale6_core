from JumpScale import j

import JumpScale.lib.sandboxer

j.application.start("jsexamples:libsandboxer")

j.tools.sandboxer.copyLibsTo("/tmp/collectd/bin","/tmp/collectd/libs",recursive=False)



j.application.stop()

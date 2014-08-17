from JumpScale import j

import JumpScale.lib.sandboxer

j.application.start("jsexamples:libsandboxer")

path="$base/apps/openjdk7/jre/bin/java"
dest="$vardir/sandbox/openjdk7/libs"
path=j.dirs.replaceTxtDirVars(path)
dest=j.dirs.replaceTxtDirVars(dest)
j.system.fs.createDir(dest)
j.tools.sandboxer.copyLibsTo(path,dest)

j.application.stop()


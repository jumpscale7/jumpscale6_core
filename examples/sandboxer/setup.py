import sys
from cx_Freeze import setup, Executable

sys.path.insert(0, "$(jumpscale.paths.base)/lib/")

dest = "/tmp/jumscalebuild"

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"],
                     "excludes": ["tkinter", "tcl", "tk", "wx", "PyQt4", "pango"], "compressed": 1, "create_shared_zip": 1,
                     "includes": ["cuisine", "fabric"],
                     "build_exe": dest}
    # "include_files":[("","lib/JumpScale")]}

base = None
if sys.platform == "linux64":
    base = "shell"

from JumpScale import j

items = [item for item in j.system.fs.listFilesInDir(".", filter="*.py") if item.find("setup.py") == -1]

items += j.system.fs.listFilesInDir("$(jumpscale.paths.base)/shellcmds/", filter="*.py")

execs = []
for item in items:
    execs.append(Executable(item, base=base))


setup(name="jumpscaleshell",
      version="6",
      description="Shell!",
      options={"build_exe": build_exe_options},
      executables=execs)


src = "/usr/lib/python2.7/JumpScale/"

j.system.fs.copyDirTree(src, "%s/lib/JumpScale/" % dest)
j.system.fs.copyDirTree("cfg", "%s/cfg/" % dest)

for item in j.system.fs.listFilesInDir(dest, True, "*.pyc"):
    j.system.fs.remove(item)

j.system.fs.removeDirTree("%s/tcl" % dest)
j.system.fs.removeDirTree("%s/tk" % dest)

j.system.fs.writeFile("%s/lib/__init__.py" % dest, "")

# now package a zip file
print "compress & put in /tmp/jumpscale.tgz"
j.system.fs.targzCompress(dest, "/tmp/jumpscale.tgz")

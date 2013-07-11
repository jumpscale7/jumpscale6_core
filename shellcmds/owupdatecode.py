from OpenWizzy import o
import OpenWizzy.baselib.mercurial
o.application.shellconfig.interactive=True

for item in o.system.fs.listDirsInDir("/opt/code/openwizzy"):
    cl=o.clients.mercurial.getClient(item)
    cl.updatemerge()
    from IPython import embed
    print "DEBUG NOW ooo"
    embed()


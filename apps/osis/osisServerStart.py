from JumpScale import j
import JumpScale.grid.osis

j.application.start("osisserver")



# from gevent import monkey
# monkey.patch_socket()
# monkey.patch_thread()

j.core.osis.startDaemon(overwriteImplementation=False)

j.application.stop()

from JumpScale import j
import JumpScale.grid.osis

# from gevent import monkey
# monkey.patch_socket()
# monkey.patch_thread()

while j.system.net.tcpPortConnectionTest("127.0.0.1",7766)==False:
    time.sleep(0.1)
    print "cannot connect to redis main, will keep on trying forever, please start redis production (port 7766)"

j.application.start("osisserver")

while j.system.net.tcpPortConnectionTest("127.0.0.1",7768)==False:
    time.sleep(0.1)
    print "cannot connect to redis, will keep on trying forever, please start redis production (port 7768)"

j.core.osis.startDaemon(overwriteImplementation=False)

j.application.stop()

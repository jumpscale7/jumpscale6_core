from JumpScale import j

descr = """
wait 10 sec
"""

name = "wait"
category = "test"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]

def action(msg):
#    import time
#    print "Print msg %s" % msg
#    print "2: print log message level 2"
#    print "2:mycat.1: print log message level 2 with a specific category"
#    print "hello world.\n%s" % msg
    print msg
    for i in range(10):
        print i
        time.sleep(0.3)
    # raise RuntimeError("test")
    msg="sleep done for %s"%msg
    j.errorconditionhandler.raiseOperationalWarning('test')

    j.logger.log("somework %s %s"%(msg,i))
    print msg
    return msg




import time
from JumpScale import j
import JumpScale.portal

j.application.start("appserver6_test")

j.logger.disable()

# q.jshellconfig.checkCreateConfigFile("blobstor")
# if "grid" not in q.jshellconfig.blobstor.getSections():
    # not configured yet
    # if not local:
        # q.jshellconfig.blobstor.setParam("grid","ip","psc.greenitglobe.com")
        # q.jshellconfig.blobstor.setParam("grid","secret","inc001")
        # q.jshellconfig.blobstor.setParam("grid","type","server")
        # q.jshellconfig.blobstor.setParam("grid","restport","9000")
        # q.jshellconfig.blobstor.setParam("grid","namespace","grid")
    # else:
        # q.jshellconfig.blobstor.setParam("grid","type","local")
        # q.jshellconfig.blobstor.setParam("grid","localpath","c:\\temp\\blobstor")
        # q.jshellconfig.blobstor.setParam("grid","namespace","grid")

j.manage.portal.startprocess()


j.application.stop()

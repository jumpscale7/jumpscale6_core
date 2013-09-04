import time
from JumpScale import j
import JumpScale.portal

j.application.start("appserver6_test")

j.logger.disable()

# q.qshellconfig.checkCreateConfigFile("blobstor")
# if "grid" not in q.qshellconfig.blobstor.getSections():
    # not configured yet
    # if not local:
        # q.qshellconfig.blobstor.setParam("grid","ip","psc.greenitglobe.com")
        # q.qshellconfig.blobstor.setParam("grid","secret","inc001")
        # q.qshellconfig.blobstor.setParam("grid","type","server")
        # q.qshellconfig.blobstor.setParam("grid","restport","9000")
        # q.qshellconfig.blobstor.setParam("grid","namespace","grid")
    # else:
        # q.qshellconfig.blobstor.setParam("grid","type","local")
        # q.qshellconfig.blobstor.setParam("grid","localpath","c:\\temp\\blobstor")
        # q.qshellconfig.blobstor.setParam("grid","namespace","grid")

j.manage.portal.startprocess()


j.application.stop()

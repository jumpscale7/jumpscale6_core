import time
from OpenWizzy import *
import OpenWizzy.portal

o.application.appname = "appserver6_test"
o.application.start()

o.logger.disable()

#q.qshellconfig.checkCreateConfigFile("blobstor")
#if "grid" not in q.qshellconfig.blobstor.getSections():
    ##not configured yet
    #if not local:
        #q.qshellconfig.blobstor.setParam("grid","ip","psc.greenitglobe.com")
        #q.qshellconfig.blobstor.setParam("grid","secret","inc001")
        #q.qshellconfig.blobstor.setParam("grid","type","server")
        #q.qshellconfig.blobstor.setParam("grid","restport","9000")
        #q.qshellconfig.blobstor.setParam("grid","namespace","grid")
    #else:
        #q.qshellconfig.blobstor.setParam("grid","type","local")
        #q.qshellconfig.blobstor.setParam("grid","localpath","c:\\temp\\blobstor")
        #q.qshellconfig.blobstor.setParam("grid","namespace","grid")

o.manage.portal.startprocess()


o.application.stop()

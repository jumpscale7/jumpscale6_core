# import socket
from JumpScale import j


class LogTargetOSIS(object):

    """
    Forwards incoming logRecords to osis
    attached to loghandler on openwizzy
    """

    def __init__(self):
        self.name = "LogToOSIS"
        from JumpScale.core.Shell import ipshellDebug, ipshell
        print "DEBUG NOW logtargetosis"
        ipshell()

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if self.serverip <> None:
            if j.system.net.tcpPortConnectionTest(self._serverip, 9200) == False:
                return False
            self.esclient = j.clients.elasticsearch.get(self._serverip, 9200)
            # j.logger.elasticsearchtarget=True

    def __str__(self):
        """ string representation of a LogTargetServer to ES"""
        return 'LogTargetLogServer logging to osis'

    __repr__ = __str__

    def log(self, logobject):
        """
        forward the already formatted message to the target destination

        """
        #@todo Low Prio: need to batch & use geventloop to timeout when used e.g. in appserver
        try:
            self.esclient.index(index="clusterlog", doc_type="logrecord", ttl="14d", replication="async", doc=logobject.toJson())
        except Exception, e:
            print "Could not log to elasticsearch server, log:\n%s" % logobject
            print "error was %s" % e

    def close(self):
        """
        Loghandlers need to implement close method
        """

    def logbatch(self, batch):
        from JumpScale.core.Shell import ipshellDebug, ipshell
        print "DEBUG NOW logbatch"
        ipshell()

    def list(self, categoryPrefix="", levelMin=0, levelMax=5, job=0, parentjob=0, private=False, nritems=500):
        from JumpScale.core.Shell import ipshellDebug, ipshell
        print "DEBUG NOW implement list using osisclient search functionality"
        ipshell()
        return result

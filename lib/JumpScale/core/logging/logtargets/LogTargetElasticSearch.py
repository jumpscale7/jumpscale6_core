# import socket
from JumpScale import j
import JumpScale.baselib.elasticsearch


class LogTargetElasticSearch(object):
    """
    Forwards incoming logRecords to elastic search
    attached to loghandler on jumpscale
    """
    def __init__(self, serverip=None,esclient=None):
        if esclient:
            self.connected = True
            self._serverip = serverip
            self.enabled = True
            self.name = "LogToES"
            self.esclient=esclient
        else:
            self.connected = False
            if serverip == None:
                serverip = "127.0.0.1"
            self._serverip = serverip
            self.enabled = self.checkTarget()
        self.name = "LogToES"

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if self._serverip:
            if j.system.net.tcpPortConnectionTest(self._serverip, 9200) == False:
                return False
            self.esclient = j.clients.elasticsearch.get(self._serverip, 9200)
            # j.logger.elasticsearchtarget=True

    def __str__(self):
        """ string representation of a LogTargetServer to ES"""
        return 'LogTargetLogServer logging to %s' % (str(self._serverip))

    __repr__ = __str__

    def log(self, logobject):
        """
        forward the already formatted message to the target destination

        """
        #@todo Low Prio: need to batch & use geventloop to timeout when used e.g. in appserver
        try:
            print("LOG OBJECT in logging to elasticsearch ", logobject)
            self.esclient.index(index="clusterlog", doc_type="logrecord", ttl="14d", replication="async", doc=logobject.__dict__)
        except Exception as e:
            raise
            print("Could not log to elasticsearch server, log:\n%s"%logobject)
            print("error was %s"%e)

    def close(self):
        """
        Loghandlers need to implement close method
        """

    def logbatch(self, batch):
        docs = []
        for logobject in batch:
            logobject.id = "%s_%s_%s_%s"%(logobject.gid, logobject.nodeid, logobject.appid, logobject.order)
            docs.append(logobject.__dict__)
        print("batch:%s"%len(docs))
        self.esclient.bulk_index(index="clusterlog", doc_type="json", docs=docs, id_field="id")

    def list(self, categoryPrefix="", levelMin=0, levelMax=5, job=0, parentjob=0, private=False, nritems=500):
        result2 = []
        Q = {'facets': {},
             'from': 0,
             'size': nritems,
             'sort': ['job', 'appid', 'order'],
             'query': { 'bool': 
                 {'must': [{'prefix': {'logrecord..category': categoryPrefix}},
                           {'range': {'logrecord.level': {'from': '%s' % levelMin, 'to': '%s' % levelMax}}},
                           {'term': {'logrecord.job': '%s' % job}},
                           {'term': {'logrecord.parentjob': '%s' % parentjob}},
                          ],
                         'must_not': [],
                         'should': []
                        } 
                      }
            }
        if private:
            Q['query']['bool']['must'].append({'term': {'json.private': '1'}})
        result = self.esclient.search(query=Q)
        for item in result["hits"]["hits"]:
            log = j.logger.getLogObjectFromDict(item["_source"])
            result2.append(log)
        return result2
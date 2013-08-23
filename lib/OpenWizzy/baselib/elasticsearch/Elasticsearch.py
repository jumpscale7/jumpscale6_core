from OpenWizzy import o
from pyelasticsearch import ElasticSearch


class ElasticsearchFactory:

    def get(self, ip="localhost", port=9200, timeout=60):
        o.logger.log("check elastic search reachable on %s on port %s" % (ip, port), level=4, category='osis.init')
        res = o.system.net.waitConnectionTest(ip, int(port), timeout)
        if res == False:
            raise RuntimeError("Could not find a running elastic server instance on %s:%s" % (ip, port))
        client = ElasticSearch('http://%s:%s/' % (ip, port))
        status = client.status()
        if not isinstance(status, dict):
            status = status()
        if status["ok"] != True:
            raise RuntimeError("Could find port of elastic server instance on %s:%s, but status was not ok." % (ip, port))
        o.logger.log("OK elastic search is reachable on %s on port %s" % (ip, port), level=4, category='osis.init')
        return client

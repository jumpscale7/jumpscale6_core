from JumpScale import j
import unittest


descr = """
test basic functioning of agentcontroller
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "agentcontroller.basic"
enable=True
priority=2

ROLE = 'node.%s.%s' % (j.application.whoAmI.gid, j.application.whoAmI.nid)

class TEST(unittest.TestCase):

    def setUp(self):
        import JumpScale.grid.agentcontroller
        self.client=j.clients.agentcontroller

    def test_basic_execution(self):
        #@todo this is just a basic test to see if agent controller works
        #execute the 4 test jumpscripts, test the right behaviour
        #did we see log (log msg in ES)
        #was there an eco in ES (search)
        #was there an eco in KVS (osis DB)
        #is it indeed waiting, so agent should be blocked
        kwargs = {'msg': 'test msg'}
        result1 = self.client.executeKwargs('jumpscale', 'echo', ROLE, kwargs=kwargs)
        self.assertEqual(result1, kwargs['msg'])

        kwargs = {'logmsg': 'test log msg'}
        self.client.executeKwargs('jumpscale', 'log', ROLE, kwargs=kwargs)
        query = {"query":{"bool":{"must":[{"term":{"category":"test_category"}}]}}}
        import JumpScale.grid.osis
        osisclient = j.core.osis.getClient(user='root')
        osis_logs = j.core.osis.getClientForCategory(osisclient, "system", "log")
        self.assertGreater( len(osis_logs.search(query)['hits']['hits']), 0)

        self.client.execute('jumpscale', 'error', ROLE, dieOnFailure=False)
        query = {"query":{"bool":{"must":[{"term":{"state":"error"}}, {"term":{"jsname":"error"}}]}}}
        osis_jobs = j.core.osis.getClientForCategory(osisclient, "system", "job")
        self.assertGreater(len(osis_jobs.search(query)['result']), 0)

        kwargs = {'msg': 'test msg', 'waittime': 5}
        result2 = self.client.executeKwargs('jumpscale', 'wait', ROLE, kwargs=kwargs)


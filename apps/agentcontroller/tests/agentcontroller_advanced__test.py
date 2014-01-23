from JumpScale import j
import time


descr = """
test advanced functioning of agentcontroller
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "agentcontroller.advanced"
enable=True
priority=8

ROLE = 'node.%s.%s' % (j.application.whoAmI.gid, j.application.whoAmI.nid)

class TEST():

    def setUp(self):
        import JumpScale.grid.agentcontroller
        self.client = j.clients.agentcontroller
        self.osisclient = j.core.osis.getClient(user='root')

    def test_queuetest1agent(self):
        #@todo launch 5 wait js (1 sec each), see they are all execute one after the other, check the logs that they were executed
        #test there is only 1 agent (use startupmanager through the processmanager)
        import JumpScale.grid.osis
        osis_logs = j.core.osis.getClientForCategory(self.osisclient, "system", "log")
        for i in range(1, 6):
            kwargs = {'msg': 'msg%s' % i, 'waittime':1}
            self.client.executeKwargs('jumpscale', 'wait', ROLE, kwargs=kwargs)
        results = list()
        for i in range(1, 6):
            query = {"category":"test_wait", "message":'msg%s' % i}
            result = osis_logs.simpleSearch(query)
            assert len(result) > 0
            results.append(result)

    def test_queuetest5agents(self):
        #start 5 agents, see that they sort of equally executed the tasks
        #jp= client.execute('jumpscale', 'jpackage_info', domain="jumpscale", timeout=10)
        pass

    def test_killbehaviour(self):
        #1 agent running
        #launch 2 jobs: wait of 5 sec test (put timeout inside of 6 sec, so if job not done after 6 sec we should be warned)
        #kill agent 
        #restart agent
        #first job should have failed
        #2nd job should still execute
        # TODO this test does not work 
        return
        kwargs = {'msg': 'test kill behavior', 'waittime':2}
        firstjob = self.client.executeKwargs('jumpscale', 'wait', ROLE, wait=False, kwargs=kwargs)
        kwargs = {'msg': 'test kill behavior', 'waittime':5}
        secondjob = self.client.executeKwargs('jumpscale', 'wait', ROLE, wait=False, kwargs=kwargs)
        j.tools.startupmanager.stopProcess('jumpscale', 'agent_0')
        j.tools.startupmanager.startProcess('jumpscale', 'agent_0')

        import JumpScale.grid.osis
        osis_jobs = j.core.osis.getClientForCategory(self.osisclient, "system", "job")
        print osis_jobs.get(secondjob['guid'])['state']
        print osis_jobs.get(firstjob['guid'])['state']
        assert osis_jobs.get(secondjob['guid'])['state'] == 'OK'
        assert osis_jobs.get(firstjob['guid'])['state'] != 'OK'

    def test_performance(self):
        #5 agents running
        #run echo test 5000 times, measure timing, put some boundaries around, there needs to be a minimal performance
        start = time.time()
        for i in range(1, 500):
            kwargs = {'msg': 'msg %s' % i}
            self.client.executeKwargs('jumpscale', 'echo', ROLE, kwargs=kwargs)
        end = time.time()
        print 'It took %s seconds to execute 500 echo jobs' % (end - start)


from JumpScale import j


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

class TEST():

    def setUp(self):
        import JumpScale.grid.agentcontroller
        self.client=j.clients.agentcontroller
                      

    def test_queuetest1agent(self):
        #@todo launch 5 wait js (1 sec each), see they are all execute one after the other, check the logs that they were executed
        #test there is only 1 agent (use startupmanager through the processmanager)
        jp= client.execute('jumpscale', 'jpackage_info', domain="jumpscale", timeout=10)

    def test_queuetest5agents(self):
        #@todo launch 50 wait js (1 sec each), see they are all execute one after the other, check the logs that they were executed
        #start 5 agents, see that they sort of equally executed the tasks
        jp= client.execute('jumpscale', 'jpackage_info', domain="jumpscale", timeout=10)

    def test_killbehaviour(self):
        #1 agent running
        #launch 2 jobs: wait of 5 sec test (put timeout inside of 6 sec, so if job not done after 6 sec we should be warned)
        #kill agent 
        #restart agent
        #first job should have failed
        #2nd job should still execute
        pass

    def test_performance(self):
        #5 agents running
        #run echo test 5000 times, measure timing, put some boundaries around, there needs to be a minimal performance
        pass


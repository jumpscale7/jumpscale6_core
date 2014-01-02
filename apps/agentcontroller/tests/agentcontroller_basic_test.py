from JumpScale import j


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

class TEST():

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
        jp= client.execute('jumpscale', 'jpackage_info', domain="jumpscale", timeout=10)

from JumpScale import j

class system_testmanager(j.code.classGetBase()):
    """
    expose test results
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="testmanager"
        self.appname="system"
        passwd = j.application.config.get("system.superadmin.passwd")
        osis = j.core.osis.getClient(j.application.config.get("grid.master.ip"), passwd=passwd)
        self.osis_test = j.core.osis.getClientForCategory(osis,"system","test")
        #system_testmanager_osis.__init__(self)
    

        pass

    def getTests(self, id=None, gid=None, nid=None, name=None, testrun=None, path=None, state=None, priority=None, organization=None, author=None, version=None, categories=None, enable=None, result=None, output=None, eco=None, source=None, **kwargs):
        """
        param:id int,, find specific id
        param:gid int,, find based on gid
        param:nid int,, find based on nid
        param:name str,,find based on name
        param:testrun str,,find based on testrun
        param:path str,,find based on path
        param:state str,,find based on state
        param:priority str,,find based on priority
        param:organization str,,find based on organization
        param:author str,,find based on author
        param:version str,,find based on version
        param:categories str,,comma separated list of categories to match against
        param:enable bool,,True,is the test enabled
        param:result json,,result of test
        param:output json,,output of test
        param:eco json,,ecos of test
        param:source json,,source of test
        result json
        """
        params = {'id': id,
                  'gid': gid,
                  'nid': nid,
                  'name': name,
                  'testrun': testrun,
                  'path': path,
                  'state': state,
                  'priority': priority,
                  'organization': organization,
                  'author': author,
                  'version': version,
                  'categories': categories,
                  'enable': enable,
                  'result': result,
                  'output': output,
                  'eco': eco,
                  }
        return self.osis_test.simpleSearch(params)
    

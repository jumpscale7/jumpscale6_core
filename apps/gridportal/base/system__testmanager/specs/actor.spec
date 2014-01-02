[actor] @dbtype:mem,fs
    """
    expose test results
    """    

    method:getTests
        """     
        """
        var:id int,, find specific id @tags: optional
        var:gid int,, find based on gid @tags: optional
        var:nid int,, find based on nid @tags: optional
        var:name str,,find based on name @tags: optional
        var:testrun str,,find based on testrun @tags: optional
        var:path str,,find based on path @tags: optional
        var:state str,,find based on state @tags: optional
        var:priority str,,find based on priority @tags: optional
        var:organization str,,find based on organization @tags: optional
        var:author str,,find based on author @tags: optional
        var:version str,,find based on version @tags: optional
        var:categories str,,comma separated list of categories to match against @tags: optional
        var:enable bool,,True,is the test enabled @tags: optional
        var:result json,,result of test @tags: optional
        var:output json,,output of test @tags: optional
        var:eco json,,ecos of test @tags: optional
        var:source json,,source of test @tags: optional
        result:json


[actor] @dbtype:mem,fs
    """
    expose test results
    """    

    method:getTests
        """     
        """
        #@todo see osis model test for all relevant properties
        var:nid int,,id of node
        var:domain str,,optional domain name for jpackage @tags: optional
        result:json


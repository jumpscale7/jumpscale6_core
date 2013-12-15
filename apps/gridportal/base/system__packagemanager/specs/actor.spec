[actor] @dbtype:mem,fs
    """
    gateway to grid
    """    
    method:getJpackages
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        lists installed, name, domain, version
        """
        var:nodeId int,,id of node
        var:domain str,,optional domain name for jpackage
        result:json

    method:getJpackage
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about 1 jpackage
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:name str,,name for jpackage
        result:json

    method:start
        """
        use agentcontroller to start a jpackage
        give good category for job so its easy to fetch info later
        return jobid
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:name str,,name for jpackage

    #do same for all other actions of jpackages


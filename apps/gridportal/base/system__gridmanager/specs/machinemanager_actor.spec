[actor] @dbtype:mem,fs
    """
    gateway to grid
    """    
    method:getProcessStats
        """     
        ask the right processmanager on right node to get the information
        """
        var:nodeId int,,id of node
        var:domain str,,optional domain name for process
        var:name str,,optional name for process
        result:json

    method:getNodeSystemStats
        """     
        ask the right processmanager on right node to get the information about node system
        """
        var:nodeId int,,id of node
        result:json

    method:getNodes
        """     
        list found nodes
        """
        result:list(list)

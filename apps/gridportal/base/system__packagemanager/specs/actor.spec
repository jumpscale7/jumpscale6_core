[actor] @dbtype:mem,fs
    """
    gateway to grid
    """    

    method:getJPackages
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        lists installed, name, domain, version
        """
        var:nid int,,id of node
        var:domain str,,optional domain name for jpackage @tags: optional
        result:json

    method:getJPackageInfo
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about 1 jpackage
        """
        var:nid int,,id of node
        var:domain str,,domain name for jpackage
        var:pname str,,name for jpackage
        #var:version str,, version of jpackage
        result:json

    method:getJPackageFilesInfo
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about files of jpackage
        """
        var:nid int,,id of node
        var:domain str,,domain name for jpackage
        var:pname str,,name for jpackage
        #var:version str,, version of jpackage
        result:json



    method:action
        """
        use agentcontroller to execute action on a jpackage
        give good category for job so its easy to fetch info later
        return jobid
        """
        var:nid int,,id of node
        var:domain str,,domain name for jpackage
        var:pname str,,name for jpackage
        #var:version str,, version of jpackage
        var:action str,, action to be executed on jpackage
        result:str


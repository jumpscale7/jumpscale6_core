[actor] @dbtype:mem,fs
    """
    gateway to grid
    """    
    method:getInstalledJPackages
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        lists installed, name, domain, version
        """
        var:nodeId int,,id of node
        var:domain str,,optional domain name for jpackage @tags: optional
        result:json

    method:getJPackage
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about 1 jpackage
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:name str,,name for jpackage
        var:version str,, version of jpackage
        result:json

    method:getPackageDescription
        """     
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns a package description
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:name str,,name for jpackage
        var:version str,, version of jpackage
        result:json

    method:action
        """
        use agentcontroller to execute action on a jpackage
        give good category for job so its easy to fetch info later
        return jobid
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:name str,,name for jpackage
        var:version str,, version of jpackage
        var:action str,, action to be executed on jpackage
        result:str

    method:getBlobs
        """
        use agentcontroller to get info files' names
        give good category for job so its easy to fetch info later
        return jobid
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:pname str,,name for jpackage
        var:version str,, version of jpackage
        result:json


    method:getBlobContents
        """
        use agentcontroller to get info file contents
        give good category for job so its easy to fetch info later
        return jobid
        """
        var:nodeId int,,id of node
        var:domain str,,domain name for jpackage
        var:pname str,,name for jpackage
        var:version str,, version of jpackage
        var:platform str,, plaftform of info file
        var:ttype str,, ttype of info file
        result:json
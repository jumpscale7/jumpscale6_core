[actor] @dbtype:mem,fs
    """
    manage the machines in a physical network
    """    
    method:initOverSSH
        """     
        will ssh into the machin and install jumpscale & bootstrap the machine
        will also fetch the info from the machine & populate local portal
        """
        var:name str,,optional name of machine
        var:organization str,,optional organization of machine
        var:ipaddr str,,ip addr to start from
        var:login str,root,login to that machine
        var:passwd str,,passwd to that machine
        result:bool    

    method:executeAction
        """     
        execute an action on a machine
        """
        var:id int,,unique id of machine
        var:name str,,name of action
        var:organization str,,name of action
        var:arguments dict,,arguments to the action (params)
        result:bool    

    method:initSelf
        """     
        init local machine into db, give optional name & org info
        """
        var:name str,,name of action
        var:organization str,,name of action
        result:bool    

[actor] @dbtype:mem
	"""
	"""    
    method:execute
        """ 
        execute a job 
        """
        var:actormethod str,,$app.$actor.$method
        var:defname str,,
        var:defcode str,,
        var:defargs str,"",
        var:name str,,    
        var:category str,"",optional category of job e.g. system.fs.copyfiles (free to be chosen)
        var:errordescr str,"",
        var:recoverydescr str,"",
        var:maxtime int,0,is max time call should take in secs
        var:defpath str,"",
        var:defagentid str,"",
        var:channel str,"",channel
        var:location str,"",location
        var:user str,"",        
        var:wait bool,True, wait till job finishes
        var:defmd5 str,"",
        result:str #jobguid


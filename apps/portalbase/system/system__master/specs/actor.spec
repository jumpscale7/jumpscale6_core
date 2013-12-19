[actor] @dbtype:mem
	"""
	"""    
    method:getAppsActors
		"""
		get dict of list of apps & actors
		"""
		var:model int,1,if you want to also get model actors; otherwise 0
        result:dict   
		
    method:registerRedisInstance
		"""
		get dict of list of apps & actors
		"""
		var:ipaddr str,,ipaddr of instance
		var:port int,,port
		var:secret str,,secret
		var:appname str,,appname
		var:actorname str,,actorname
        result:dict   
		
    method:ping @nokey
		"""
		just a simple ping to the service (returns pong)
		"""
        result:str    

    method:echo @nokey
		"""
		just a simple echo service
		"""        
		var:input str,,result will be same as this input
		result:str

    method:waitForJob
        """
        waits for a job to execute
        """
        var:jobid int,,
        var:timeout int,,	@tags: optional
        result:dict

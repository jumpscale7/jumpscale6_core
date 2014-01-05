[actor] @dbtype:mem
	"""
	this actor manages all content on the wiki
	can e.g. notify wiki/appserver of updates of content
	"""    
    method:notifyFiledir
		"""		
		"""
		var:path str,,path of content which got changed
        result:bool    

    method:getSpaces
		"""		
		"""
        result:list(str)
		
    method:getSpacesWithPaths
		"""		
		"""
        result:list([name,path])

    method:getContentDirsWithPaths
		"""		
		return root dirs of content (actors,buckets,spaces)
		"""
        result:list([name,path])

    method:getBucketsWithPaths
		"""		
		"""
        result:list([name,path])
 
    method:getActorsWithPaths
        """		
        """
        result:list([name,path])
 
    method:getBuckets
		"""		
		"""
        result:list(str)

    method:getActors
		"""		
		"""
        result:list(str)


    method:notifySpaceModification
		"""		
		"""
		var:id str,,id of space which changed
        result:bool    

    method:notifySpaceNew
		"""		
		"""
		var:path str,,path of content which got changed
		var:name str,,name 
		result:bool    

    method:notifySpaceDelete
		"""		
		"""
		var:id str,,id of space which changed
		result:bool    

    method:notifyBucketDelete
		"""		
		"""
		var:id str,,id of bucket which changed
		result:bool  

    method:notifyBucketModification
		"""		
		"""
		var:id str,,id of bucket which changed
        result:bool    

    method:notifyBucketNew
		"""		
		"""
		var:path str,,path of content which got changed
		var:name str,,name 
		result:bool    

    method:notifyActorNew
		"""		
		"""
		var:path str,,path of content which got changed
		var:name str,,name 
		result:bool 

    method:notifyActorModification
		"""		
		"""
		var:id str,,id of actor which changed
        result:bool  

    method:notifyActorDelete
		"""		
		"""
		var:id str,,id of space which changed
		result:bool 


    method:prepareActorSpecs
		"""		
		compress specs for specific actor and targz in appropriate download location
		"""
		var:app str,,name of app
		var:actor str,,name of actor
		result:bool    

    method:wikisave @nokey
		"""		
		"""
		var:authkey str,,key to authenticate doc
		var:text str,,content of file to edit
        result:bool  


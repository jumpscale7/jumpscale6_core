[actor] @dbtype:fs
	"""
	manipulate our virtual filesystem
	"""    

    method:listdir
        """     
        """
        var:path str,,path of dir in unified namespace
        result:list(str) #the str is D|dirname|dirguid or F|name|md5

    method:filedelete
        """     
        """
        var:path str,,path of file in unified namespace
        var:user str,,user who modified the file
        result:bool    

    method:filenew
        """     
        """
        var:path str,,path of new file in unified namespace
        var:user str,,user who modified the file
        result:str #$contentguid which is reference to content

    method:filemod
        """     
        """
        var:path str,,path of new file in unified namespace
        var:user str,,user who modified the file
        result:str #$contentguid which is reference to content

    method:dirdelete
        """     
        """
        var:path str,,path of dir in unified namespace
        var:recursive bool,True,if true will delete all files & dirs underneath
        var:user str,,user who modified the file
        result:bool

    method:getdirobject
        """
        """
        var:id str,,unique id for dir object (is dirguid which is md5 path)
        result:str #json representation of full object


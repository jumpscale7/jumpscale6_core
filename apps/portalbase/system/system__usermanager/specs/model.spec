[rootmodel:user] @dbtype:fs
    """
    user
    """
    prop:id str,,is unique id =name 
    prop:passwd str,, 
    prop:secret str,,
    prop:emails list(str),,list email addresses #@list
    prop:groups list(str),, [groupname] #@list

[rootmodel:group] @dbtype:fs
    """
    group of users
    """
    prop:id str,,is unique id =name 
    prop:members list(str),,list members of group [username] #@list
    prop:system bool,False,



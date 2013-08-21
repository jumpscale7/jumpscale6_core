

[rootmodel:actor] @dbtype:mem #@index
    """
    actor location on disk
    """
    prop:application str,,
    prop:actor str,,
    prop:id str,,is application__actor @list
    prop:path str,,
    prop:acl dict(str),,dict with key the group or username; and the value is a string


[rootmodel:space] @dbtype:mem #@index
    """
    space
    """
    prop:id str,,is name of space @list
    prop:path str,,
    prop:acl dict(str),,dict with key the group or username; and the value is a string
    
[rootmodel:bucket] @dbtype:mem #@index
    """
    bucket
    """
    prop:id str,, #test  @list
    prop:path str,, @list
    prop:acl dict(str),,dict with key the group or username; and the value is a string
    
    

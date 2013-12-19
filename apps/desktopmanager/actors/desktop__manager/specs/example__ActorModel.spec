[rootmodel:user] #@index
    """
    group of users
    """
    prop:guid str,,is guid
    prop:id int,,is unique id 
    prop:domain str,,domain
    prop:name str,,
    prop:emails list(str),,list email addresses

[rootmodel:group] #@index
    """
    group of users
    """
    prop:guid str,,is guid
    prop:id int,,is unique id 
    prop:domain str,,domain
    prop:name str,,
    prop:members list(user),,list members if group



[rootmodel:user] @index
    """
    group of users
    """
    #prop:guid str,,is guid
    prop:id int,,is unique id 
    prop:organization str,,domain
    prop:name str,,
    prop:emails list(str),,list email addresses
    prop:groups list(str),,which groups are we linked to


[rootmodel:group] @index
    """
    group of users
    """
    #prop:guid str,,is guid
    prop:id int,,is unique id 
    prop:name str,,

[rootmodel:project] @index
    """
    project
    """
    #prop:guid str,,is guid
    prop:id int,,is unique id 
    prop:name str,,domain
    prop:descr str,,
    prop:organizations list(str),,which organizations is proj linked to
    prop:tasks list(task),,

[model:task] @index
    """
    task for a user
    """
    prop:id int,,is unique id 
    prop:name str,,
    prop:description str,,
    prop:priority int,,level 1-9 1 is most urgent
    prop:project str,,link to project
    prop:type str,,type comes from table tasktype and is grouped per project
    prop:urgency str,,TODAY WEEK MONTH LATER
    prop:taskowner str,,owner of task (user)
    prop:members list(str),,list members if group

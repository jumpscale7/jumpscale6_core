

[rootmodel:actorinstance] @nocrud dbmem
    """
    1 actor instance (id is appname__actorname__instance)
    """
    prop:instance int,0,0 is master for the actor; 1+ is an instance of the actor
    prop:start int,,is epoch start
    prop:appname str,,name of application
    prop:actorname str,,name of actor
    prop:ismodel bool,False,
    prop:appserverid int,,
    prop:redisclusterid int,,
    prop:arakoonclusterid int,,
    
[model:appserver] 
    """
    1 appserver instance 
    """
    prop:id int,, 
    prop:start int,,is epoch start
    prop:lastnotified int,,is epoch of last notification when we knew appserver was alive
    prop:host str,,ip addr:port of server
    prop:secret str,,
    
[model:rediscluster]
    """
    1 rediscluster instance
    """
    prop:id int,,
    prop:start int,,is epoch start
    prop:lastnotified int,,is epoch of last notification when we knew rediscluster was alive
    prop:hosts list(str),,ip addr:port of servers
    prop:secret str,,
    
[model:arakooncluster] 
    """
    1 arakoon cluster instance
    """
    prop:id int,, @list
    prop:start int,,is epoch start
    prop:lastnotified int,,is epoch of last notification when we knew arakoon was alive
    prop:hosts list(str),,ip addr:port of servers
    prop:secret str,,

[rootmodel:gridmap] @nocrud dbmem
    prop:id int,,there is only 1; and id = 0
    prop:appservers list(appserver),,
    prop:redisclusters list(rediscluster),,
    prop:arakoonclusters list(arakooncluster),,
    prop:actorinstances dict(actorinstance),,key is appname__actorname__instance
    prop:actor2redis dict(int),,key is appname__actorname the value is key of rediscluster
    prop:version int,,version of the gridmap
    prop:master str,,in format ipaddr:port
    
    
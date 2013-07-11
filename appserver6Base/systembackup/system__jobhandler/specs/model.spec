
# [enumeration:jobstate]
#     """
#     type of jobstate, not used for now
#     """
#     OK
#     STARTED
#     ABORTED
#     ERROR
#     TIMEOUT

# [rootmodel:job] #@index
#     """
#     1 job
#     """
#     prop:guid str,,is id for job
#     prop:id str,,is unique id for job (only unique in combination with methodid)
#     prop:actormethod str,"",$app.$actor.$method
#     prop:defname str,"",
#     prop:defcode str,"",
#     prop:defpath str,"",
#     prop:defargs str,"",
#     prop:defagentid str,"",
#     prop:defmd5 str,"",
#     prop:name str,"",    
#     prop:category str,"",optional category of job e.g. system.fs.copyfiles (free to be chosen)
#     prop:errordescr str,"",
#     prop:recoverydescr str,"",
#     prop:maxtime int,0,is max time call should take in secs
#     prop:start int,0,is epoch start
#     prop:stop int,0,is epoch stop
#     prop:state str,"init",state e.g. init,ok;started;aborted;error;timeout
#     prop:channel str,"",channel
#     prop:location str,"",location
#     prop:user str,"",


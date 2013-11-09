def main(j,args,params,tags,tasklet):
   
    #gather statistics to do with your app, standard they will be collected every 5 min

    #example:
    #q.monitoring.stats.log("$(node.name).$(qp.name).iops 1000")
    
    params.result=True 
    return params
    
    
def match(j,args,params,tags,tasklet):
    return True
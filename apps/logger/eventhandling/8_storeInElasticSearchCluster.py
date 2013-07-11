
def main(q,args,params,tags,tasklet):
   
	event=args["event"]
	esclient=q.core.grid.esclient

	from pylabs.Shell import ipshellDebug,ipshell
	print "DEBUG NOW elastic search store event"
	ipshell()

	return params


def match(q,args,params,tags,tasklet):
    return False  


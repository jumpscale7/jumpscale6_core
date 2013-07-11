
def main(q,args,params,tags,tasklet):

	from pylabs.Shell import ipshellDebug,ipshell
	print "DEBUG NOW log es, no longer supported, fix if required, new logobject format"
	ipshell()
	
	q.core.grid.logger.elasticsearch.logbatch(args.logbatch) 
	
	return params


def match(q,args,params,tags,tasklet):
    return q.core.grid.logger.elasticsearch<>None


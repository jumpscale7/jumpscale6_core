
def main(q,args,params,tags,tasklet):
   

	q.core.grid.logger.osiseco.set(args["eco"].__dict__, compress=False)

	return params


def match(q,args,params,tags,tasklet):
    return True


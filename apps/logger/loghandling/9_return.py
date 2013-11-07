
def main(q, args, params, tags, tasklet):

    params.result = args.logobj
    
    args.logger.logQueue.put(args.logobj)

    return params


def match(q, args, params, tags, tasklet):
    return True


def main(q, args, params, tags, tasklet):
    q.core.grid.logger.elasticsearch.logbatch(args.logbatch)

    return params


def match(q, args, params, tags, tasklet):
    return q.core.grid.logger.elasticsearch <> None

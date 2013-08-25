
def main(q, args, params, tags, tasklet):

    q.core.grid.logger.osis.set(params.batchListDictSerialized, compress=False)

    return params


def match(q, args, params, tags, tasklet):
    return q.core.grid.logger.osis <> None

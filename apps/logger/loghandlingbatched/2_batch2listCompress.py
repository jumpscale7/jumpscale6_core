
def main(q, args, params, tags, tasklet):

    # params.batchListDict=[]
    # for item in args.logbatch:
    # 	params.batchListDict.append(item.__dict__)

    params.batchListDictSerialized = q.db.serializers.ujson.dumps(args.logbatch)

    return params


def match(q, args, params, tags, tasklet):
    return q.core.grid.logger.osis <> None

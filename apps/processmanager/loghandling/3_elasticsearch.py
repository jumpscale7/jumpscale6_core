GLOB = dict()

def main(q, args, params, tags, tasklet):
    if 'logger' not in GLOB:
        from JumpScale.core.logging.logtargets.LogTargetElasticSearch import LogTargetElasticSearch
        GLOB['logger'] = LogTargetElasticSearch('127.0.0.1')
    GLOB['logger'].log(args.logobj)
    return params


def match(q, args, params, tags, tasklet):
    return False

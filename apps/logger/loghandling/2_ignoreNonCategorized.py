
def main(q, args, params, tags, tasklet):

    if args.logobj.category == "":
        params.stop = True

    return params


def match(q, args, params, tags, tasklet):
    return True


def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags

    
    p=args.tags.getDict()

    out='!/restmachine/system/gridmanager/getStatImage?statKey=%s&_png=1&width=%s&height=%s&.png!'%(p["key"],p["width"],p["height"])
    
    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

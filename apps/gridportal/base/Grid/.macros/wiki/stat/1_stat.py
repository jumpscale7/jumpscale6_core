
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags
    
    p=args.tags.getDict()

    stattype = p['stattype'] if p.get('stattype') and not p['stattype'].startswith('$$') else None

    if stattype == 'node':
        out='!/restmachine/system/gridmanager/getStatImage?statKey=%s&_png=1&width=%s&height=%s&.png!'%(p["key"],p["width"],p["height"])
    elif stattype == 'process':
        out='!/restmachine/system/gridmanager/getStatImage?statKey=%s&_png=1&width=%s&height=%s&.png!'%(p["key"],p["width"],p["height"])
    else:
        out = 'Stat type invalid'
    
    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

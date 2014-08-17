
def main(o, args, params, tags, tasklet):

    params.merge(args)

    page = params.page
    tags = params.tags

    for item in j.core.portal.active.bucketsloader.buckets.keys():
        params.page.addBullet(item, 1)

    return params


def match(o, args, params, tags, tasklet):
    return True

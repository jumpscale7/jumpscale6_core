
def main(j, args, params, tags, tasklet):

    params.merge(args)

    page = params.page
    tags = params.tags

    for item in j.core.portal.runningPortal.webserver.bucketsloader.buckets.keys():
        params.page.addBullet(item, 1)

    return params


def match(j, args, params, tags, tasklet):
    return True

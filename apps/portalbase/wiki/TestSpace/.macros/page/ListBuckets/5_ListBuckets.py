
def main(o, args, params, tags, tasklet):

    params.merge(args)
    
    page=params.page
    tags=params.tags
    
    for item in o.core.portal.runningPortal.webserver.bucketsloader.buckets.keys():
        params.page.addBullet(item,1)
    
    return params


def match(o, args, params, tags, tasklet):
    return True


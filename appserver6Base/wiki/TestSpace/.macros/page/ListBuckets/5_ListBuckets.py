
def main(q, args, params, tags, tasklet):

    params.merge(args)
    
    page=params.page
    tags=params.tags
    
    for item in q.core.appserver6.runningAppserver.webserver.bucketsloader.buckets.keys():
        params.page.addBullet(item,1)
    
    return params


def match(q, args, params, tags, tasklet):
    return True


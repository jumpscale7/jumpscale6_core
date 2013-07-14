
def main(o,args,params,tags,tasklet):
    import os
    page = args.page
    params.result = page

    if args.tags.tagExists("path"):
        path=args.tags.tagGet("path").replace("+",":").replace("___",":").replace("\\","/")
        if not o.system.fs.exists(path):
            page.addMessage("ERROR:could not find file %s"%path)

        apppath = o.core.portal.runningPortal.cfgdir.rpartition('/')[0]
        codepath = os.getcwd()
        if path.startswith('/') and not (path.startswith(apppath) or path.startswith(codepath)):
            path=''

    else:
        path=""

    if  args.tags.tagExists("bucket"):
        bucket=args.tags.tagGet("bucket").lower()

        if not o.core.portal.runningPortal.webserver.bucketsloader.buckets.has_key(bucket):
            page.addMessage("Could not find bucket %s" % bucket)
            return params
        bucket=o.core.portal.runningPortal.webserver.bucketsloader.buckets[bucket]
        path=bucket.model.path.replace("\\","/")

    if  args.tags.tagExists("height"):
        height=int(args.tags.tagGet("height"))
    else:
        height=500

    if  args.tags.tagExists("key"):
        key=args.tags.tagGet("key")
    else:
        key=None



    if  args.tags.tagExists("readonly") or args.tags.labelExists("readonly"):
        readonly=True
    else:
        readonly=False

    if o.apps.system.usermanager.extensions.usermanager.checkUserIsAdminFromCTX(args.requestContext):
        readonly=False

    if  args.tags.tagExists("tree") or args.tags.labelExists("tree"):
        tree=True
    else:
        tree=False


    if path=="$$path":
        params.page.addMessage("Could not find path to display explorer for")
        return params

    page.addExplorer(path,dockey=key,height=height,readonly=readonly,tree=tree)


    return params


def match(q,args,params,tags,tasklet):
    return True

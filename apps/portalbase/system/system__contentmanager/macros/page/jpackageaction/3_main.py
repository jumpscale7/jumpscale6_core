def main(j, args, params, tags, tasklet):
    page = args.page
    action = args.requestContext.params.get('action')
    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    if version:
        package = j.packages.find(domain, name, version)[0]
    else:
        package = j.packages.findNewest(domain, name)

    message = "%s on %s successful" % (action, name)

    if hasattr(package, action):
        getattr(package, action)()
    else:
        message = "%s on %s failed" % (action, name)

    page.addHTML(message)


    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True
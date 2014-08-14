def main(j, args, params, tags, tasklet):
    page = args.page
    action = args.requestContext.params.get('action')
    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    if not nid:
        nid = j.application.whoAmI.nid
    message = j.apps.system.packagemanager.action(nid=nid, domain=domain, pname=name, version=version, action=action)

    page.addHTML(message)


    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True

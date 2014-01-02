def main(j, args, params, tags, tasklet):
    page = args.page
    action = args.requestContext.params.get('action')
    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    j.core.portal.runningPortal.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        _, nid, _ = j.application.whoAmI
    result = j.apps.system.packagemanager.action(nid=nid, domain=domain, pname=name, version=version, action=action)['result']

    import json
    message = json.loads(result)['result']

    page.addHTML(message)


    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True
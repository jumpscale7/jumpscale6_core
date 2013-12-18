
def main(j, args, params, tags, tasklet):
    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nodeId')

    j.core.portal.runningPortal.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        _, nid, _ = j.application.whoAmI
    description = j.apps.system.packagemanager.getPackageDescription(nodeId=nid, domain=domain, pname=name, version=version)['result']

    import json
    out = json.loads(description)['result']

    params.result = (out, args.doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

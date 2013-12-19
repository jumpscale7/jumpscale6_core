
def main(j, args, params, tags, tasklet):
    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')
    nid = args.requestContext.params.get('nid')

    actor=j.core.portal.runningPortal.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        _, nid, _ = j.application.whoAmI
    
    jp=actor.getJPackage(nodeId=nid, domain=domain, pname=name, version=version)

    if jp==None:
        out= "h3. Could not find package:%s %s (%s) installed on node:%s"%(domain,name,version,nid)
        params.result = (out, args.doc)
        return params

    import json
    result = json.loads(result)

    # if result == False:
    #     page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
    #     params.result = page
    #     return params
    
    
    out+="h2. %s\n"%jp['name']
    out+="* Installed: %s\n" % (jp['isInstalled'])
    info = ('domain', 'version', 'buildNr', 'description')
    for i in info:
        out+='* %s: %s\n' % (i.capitalize(), jp[i])

    out+="Supported platforms: %s" % ', '.join([x for x in result['supportedPlatforms']])

    out+="h2. Dependencies\n"
    dependencies = sorted(result['dependencies'], key=lambda x: x.name)
    for dep in dependencies:
        href = '/jpackages/JPackageShow?domain=%s&name=%s&version=%s' % (dep.domain, dep.name, dep.version)
        out+="* [%s|%s]\n" % (href, dep.name)

    


    C="""
h2. Explorers

|[JPackage Code Editors|/jpackages/JPackageCodeEditors?domain=$$domain&name=$$name&version=$$version]|
|[JPackage Browser|/jpackages/JPackageBrowser?domain=$$domain&name=$$name&version=$$version]|
|[JPackage Files|/jpackages/JPackageFiles?domain=$$domain&name=$$name&version=$$version]|
"""

    C="""
h2. Actions

|[start|/jpackages/JPackageAction?action=start&domain=$$domain&name=$$name&version=$$version]|
|[stop|/jpackages/JPackageAction?action=stop&domain=$$domain&name=$$name&version=$$version]|
|[restart|/jpackages/JPackageAction?action=restart&domain=$$domain&name=$$name&version=$$version]|
|[update|/jpackages/JPackageAction?action=update&domain=$$domain&name=$$name&version=$$version]|
|[package|/jpackages/JPackageAction?action=package&domain=$$domain&name=$$name&version=$$version]|
|[upload|/jpackages/JPackageAction?action=upload&domain=$$domain&name=$$name&version=$$version]|
"""

    C="""
h2. Description

{{jpackagedescr}}
"""




    import json
    out = json.loads(description)['result']

    params.result = (out, args.doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

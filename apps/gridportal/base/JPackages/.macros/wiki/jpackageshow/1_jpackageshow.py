
def main(j, args, params, tags, tasklet):
    domain = args.getTag('domain')
    name = args.getTag('name')
    version = args.getTag('version')
    nid = args.getTag('nid')

    actor = j.apps.actorsloader.getActor('system', 'packagemanager')

    if not nid:
        nid = j.application.whoAmI.nid

    jp = actor.getJPackages(nid=nid, domain=domain, pname=name, version=version)
    out = ''
    if not jp:
        out= "h3. Could not find package:%s %s (%s) installed on node:%s"%(domain,name,version,nid)
        params.result = (out, args.doc)
        return params

    # if result == False:
    #     page.addHTML("<script>window.open('/jpackages/jpackages', '_self', '');</script>" )
    #     params.result = page
    #     return params
   
    jp = actor.getJPackageInfo(nid=nid, domain=domain, pname=name, version=version)
    
    out += "h2. JPackage: %s\n"%jp['name']
    # for i in info:
    out += '|*Domain*|%s|*Installed*|%s|\n' % (jp['domain'], jp['isInstalled'])
    out += "|*Version*|%s|*Supported platforms*|%s|\n" % (jp['version'], ', '.join([x for x in jp['supportedPlatforms']]))
    out += '|*Build Number*|%s|||' % jp['buildNr']

    out += 'h3. Description\n'
    descr = jp['description'].replace('$(jp.name)', jp['name'])
    descr = descr.replace('$(jp.version)', jp['version'])
    descr = descr.replace('$(jp.description)', '')
    out +=  descr + "\n"

    out+="h3. Dependencies\n"
    dependencies = sorted(jp['dependencies'], key=lambda x: x.name)
    for dep in dependencies:
        href = '/jpackages/JPackageShow?nid=%s&domain=%s&name=%s&version=%s' % (nid, dep.domain, dep.name, dep.version)
        out+="* [%s|%s]\n" % (href, dep.name)

    jp['nid'] = nid
    out+="""
h3. Explorers

|[JPackage Code Editors|/jpackages/JPackageCodeEditors?nid=%(nid)s&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[JPackage Browser|/jpackages/JPackageBrowser?nid=%(nid)s&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[JPackage Files|/jpackages/JPackageFiles?nid=%(nid)s&domain=%(domain)s&name=%(name)s&version=%(version)s]|
""" % jp

    out+="""
h3. Actions

|[Start|/jpackages/JPackageAction?action=start&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[Stop|/jpackages/JPackageAction?action=stop&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[Restart|/jpackages/JPackageAction?action=restart&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[Update|/jpackages/JPackageAction?action=update&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[Package|/jpackages/JPackageAction?action=package&domain=%(domain)s&name=%(name)s&version=%(version)s]|
|[Upload|/jpackages/JPackageAction?action=upload&domain=%(domain)s&name=%(name)s&version=%(version)s]|
""" % jp

    params.result = (out, args.doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

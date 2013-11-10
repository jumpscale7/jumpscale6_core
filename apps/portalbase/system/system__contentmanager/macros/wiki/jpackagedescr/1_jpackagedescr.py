
def main(j, args, params, tags, tasklet):
    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    # if version:
    #     package = j.packages.find(domain, name, version)[0]
    # else:
    #     package = j.packages.findNewest(domain, name)    

    j.packages.docGenerator.getDocs()

    if not j.packages.docGenerator.docs.existsPackage(domain,name,version):
        out="ERROR:COULD NOT FIND PACKAGE:%s %s %s"%(domain,name,version)
        params.result = (out, args.doc)
        return params

    jp=j.packages.docGenerator.docs.getPackage(domain,name,version)

    out=jp.getDescr()

    params.result = (out, args.doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

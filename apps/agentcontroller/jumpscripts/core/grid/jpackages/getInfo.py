from JumpScale import j

descr = """gets jpackage info"""

name = "jpackage_info"
category = "jpackages"
organization = "jumpscale"
author = "khamisr@incubaid.com"
version = "1.0"

gid, nid, _ = j.application.whoAmI
roles = []


def action(domain, pname, version):
    
    if version and domain and pname:
        package = j.packages.find(domain, pname, version)[0]
    else:
        if domain and pname:
            package = j.packages.findNewest(domain, pname)
            if not package:
                return False
        else:
            return False

    result = dict()
    fields = ('buildNr', 'debug', 'dependencies','domain',
              'name', 'startupTime', 'supportedPlatforms',
              'taskletsChecksum', 'tcpPorts', 'version','tags','version')

    for field in fields:
        result[field] = getattr(package, field)

    result['isInstalled'] = package.isInstalled()
    result['codeLocations'] = package.getCodeLocationsFromRecipe()
    result['metadataPath'] = package.getPathMetadata()
    result['filesPath'] = package.getPathFiles()
    recipe=package.getCodeMgmtRecipe()            
    lines=[line for line in j.system.fs.fileGetContents(recipe.configpath).split("\n") if (line.strip()<>"" and line.strip()[0]<>"#")]
    result['coderecipe']="\n".join(lines)
    result['description'] = j.system.fs.fileGetContents("%s/description.wiki"%package.getPathMetadata())
    result["buildNrInstalled"]=package.getHighestInstalledBuildNr()


    return result

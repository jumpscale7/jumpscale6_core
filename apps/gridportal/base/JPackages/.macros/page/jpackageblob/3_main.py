def main(j, args, params, tags, tasklet):

    page = args.page

    domain = args.requestContext.params.get('domain')
    name = args.requestContext.params.get('name')
    version = args.requestContext.params.get('version')

    if version:
        package = j.packages.find(domain, name, version)[0]
    else:
        package = j.packages.findNewest(domain, name)
    
    page.addHeading('Files', 2)
    blobpaths = j.system.fs.joinPaths(j.dirs.packageDir, "metadata", domain, name, version, "files")
    blobs = j.system.fs.find(blobpaths, '*.info')
    for blob in blobs:
        platform = blob.split('___')[0]
        ttype = blob.split('___')[1].split('.info')[0]
        blobinfo = package.getBlobInfo(platform, ttype)

        #@todo P3 not very nice, should have been a wiki macro, outputting wiki

        page.addHeading("Platform:%s &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Blobstor Key:%s" % (platform.capitalize(), blobinfo[0]), 5)
        page.addHTML("""<table class="table table-striped table-bordered dataTable" id="example" border="0" cellpadding="0" cellspacing="0" width="100%" aria-describedby="example_info" style="width: 100%;">""")
        page.addHTML("""<thead><tr role="row"><th role="columnheader" tabindex="0" aria-controls="example" rowspan="1" colspan="1" style="width: 70%%;" aria-sort="ascending">File (%s)</th>""" % ttype)
        page.addHTML("""<th role="columnheader" tabindex="0" aria-controls="example" rowspan="1" colspan="1" style="width: 30%" aria-sort="ascending">MD5 Checksum</th></tr></thead>""")
        page.addHTML("""<tbody role="alert" aria-live="polite" aria-relevant="all">""")

        for entry in blobinfo[1]:
            md5chksum = entry[0]
            filepath = entry[1]
            page.addHTML("""<tr><td>%s</td><td>%s</td></tr>""" % (filepath, md5chksum))
        page.addHTML("""</tbody></table>""")

    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True

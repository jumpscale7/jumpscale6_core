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
    blobinfo = package.getBlobInfo()
    for platform, blobmetadata in blobinfo.iteritems():
        page.addHeading(platform.capitalize(), 4)
        page.addHTML("""<table class="table table-striped table-bordered dataTable" id="example" border="0" cellpadding="0" cellspacing="0" width="100%" aria-describedby="example_info" style="width: 100%;">""")
        page.addHTML("""<thead><tr role="row"><th role="columnheader" tabindex="0" aria-controls="example" rowspan="1" colspan="1" style="width: 70%;" aria-sort="ascending">File</th>""")
        page.addHTML("""<th role="columnheader" tabindex="0" aria-controls="example" rowspan="1" colspan="1" style="width: 30%" aria-sort="ascending">MD5 Checksum</th></tr></thead>""")
        page.addHTML("""<tbody role="alert" aria-live="polite" aria-relevant="all">""")
        for fdata in blobmetadata.paths:
            md5chksum = fdata[0]
            filepath = fdata[1]
            page.addHTML("""<tr><td>%s</td><td>%s</td></tr>""" % (filepath, md5chksum))
        page.addHTML("""</tbody></table>""")

    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True

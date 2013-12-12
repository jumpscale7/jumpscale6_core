def main(j, args, params, tags, tasklet):

    page = args.page
    qsparams = args.requestContext.params
    path = qsparams.pop('path', None)
    rights = qsparams.pop('rights', None)

    modifier = j.html.getPageModifierGridDataTables(page)
    url = '/restmachine/system/logs/listJobs?'
    for p, pval in qsparams.iteritems():
        url += '%s=%s&' % (p, pval)

    fieldnames = ('JSName', 'JSOrganization', 'Parent', 'Roles', 'State', 'Message', 'Result')
    page = modifier.addTableFromURL(url, fieldnames)

    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True

import re

def main(j, args, inparams, tags, tasklet):
    page = args.page
    doc = args.doc
    pagename = doc.original_name.lower()
    breadcrumbs = [('/grid/', 'Grid'), ]
    params = args.requestContext.params.copy()


    if pagename == 'nic':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('nics?nid=%s' % nid, 'NICs'))
        breadcrumbs.append(('nic?id=%(id)s' % params, params['nic']))
        params['id'] = params['nid']
        pagename = 'node'
    elif pagename == 'job':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('jobs?nid=%s' % nid, 'Jobs'))
        breadcrumbs.append(('job?id=%(id)s' % params, 'Job %s' % params['id']))
        params['id'] = nid
        pagename = 'node'
    elif pagename == 'disk':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('disks?nid=%s' % nid, 'Disks'))
        breadcrumbs.append(('disk?id=%(id)s' % params, doc.appliedparams.get('path', '')))
        params['id'] = nid
        pagename = 'node'
    elif pagename == 'machine':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('machines?nid=%s' % nid, 'Machines'))
        breadcrumbs.append(('machine?id=%(id)s' % params, doc.appliedparams.get('name', '')))
        params['id'] = nid
        pagename = 'node'
    elif pagename == 'process':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('processes?nid=%s' % nid, 'Processes'))
        breadcrumbs.append(('process?id=%(id)s' % params, doc.appliedparams.get('name', '')))
        params['id'] = nid
        pagename = 'node'
    elif pagename == 'log':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('logs?nid=%s' % nid, 'Logs'))
        breadcrumbs.append(('log?id=%(id)s' % params, 'Log %s' % params['id']))
        params['id'] = nid
        pagename = 'node'
    elif pagename == 'eco':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('ecos?nid=%s' % nid, 'ECOs'))
        breadcrumbs.append(('eco?id=%(id)s' % params, 'ECO %s' % params['id']))
        params['id'] = nid
        pagename = 'node'
    elif pagename in ('machines', 'nics', 'jobs', 'processes', 'logs', 'ecos'):
        nid = params.get('nid')
        breadcrumbs.append(('%s?nid=%s' % (pagename, nid), doc.original_name))
        params['id'] = nid
        pagename = 'node'

    if pagename == 'node' and params.get('id'):
        nid = params.get('id')
        breadcrumbs.insert(1, ('Nodes', 'Nodes'))
        breadcrumbs.insert(2, ('node?id=%s' % nid, 'Node %s' % nid))

    if pagename == 'nodes':
        breadcrumbs.insert(1, ('Nodes', 'Nodes'))

    data = "<ul class='breadcrumb'>%s</ul>"
    innerdata = ""
    for link, title in breadcrumbs[:-1]:
        innerdata += "<li><a href='%s'>%s</a><span style='opacity: 0.5; margin-right: 8px; margin-left: 2px;' class='icon-chevron-right'></span></li>" % (link, title)
    innerdata += "<li class='active'>%s</li>" % breadcrumbs[-1][1]

    page.addMessage(data % innerdata)
    inparams.result = page
    return inparams


def match(j, args, params, tags, tasklet):
    return True

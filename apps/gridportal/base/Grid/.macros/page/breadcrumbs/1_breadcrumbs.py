import re

def main(j, args, inparams, tags, tasklet):
    page = args.page
    doc = args.doc
    page.addCSS('/lib/breadcrumbs/breadcrumbs.css')    

    pagename = doc.original_name.lower()
    separator = '<i class="separator"></i>'
    breadcrumbs = [('', 'Grid'), ('Nodes', 'Nodes')]
    params = args.requestContext.params.copy()


    if pagename == 'nic':
        nid = doc.appliedparams.get('nid')
        breadcrumbs.append(('nics?nid=%s' % nid, 'NICs'))
        breadcrumbs.append(('nic?id=%(id)s&nic=%(nic)s&nid=%(nid)s' % params, params['nic']))
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
        breadcrumbs.append(('process?id=%(id)s' % params, doc.appliedparams['pname']))
        params['id'] = nid
        pagename = 'node'
    elif pagename in ('machines', 'nics', 'jobs', 'processes'):
        nid = params.get('nid')
        breadcrumbs.append(('%s?nid=%s' % (pagename, nid), doc.original_name))
        params['id'] = nid
        pagename = 'node'

    if pagename == 'node' and params.get('id'):
        nid = params.get('id')
        breadcrumbs.insert(2, ('node?id=%s' % nid, 'Node %s' % nid))

    page.addMessage(separator.join('<a href="/Grid/{0}">{1}</a>'.format(link, title) for link, title in breadcrumbs))
    inparams.result = page
    return inparams


def match(j, args, params, tags, tasklet):
    return True

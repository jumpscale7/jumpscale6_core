def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc

    id = args.getTag('id')
    actor=j.apps.system.gridmanager
    width = args.getTag('width', 800)
    height = args.getTag('height', 400)

    if not id:
        out = 'Missing process id param "id"'
        params.result = (out, doc)
        return params

    _data = {'height':height, 'width':width}
    
    cpustats = args.tags.labelExists("cpustats")
    iostats = args.tags.labelExists("iostats")
    memstats = args.tags.labelExists("memstats")
    threadingstats = args.tags.labelExists("threadingstats")
    
    out = ''
    obj = actor.getProcesses(id=id)
    if not obj:
        out = 'No process with id %s found' % id
        params.result = (out, doc)
        return params

    obj = obj[0]
    prockey = "n%s.process.%%s.%%s" % obj['nid']
    if obj['type'] == 'jsprocess':
        prockey = prockey % ('js', "%s_%s" % (obj['jpdomain'], obj['sname']))
    else:
        prockey = prockey % ('os', "%s" % (obj['sname']))

    _data['prockey'] = prockey

    if cpustats:
        out += '\nh5. CPU Statistics\n'
        out += '{{stat key:%(prockey)s.cpu_percent width:%(width)s height:%(height)s}}<br><br>' % _data
    if iostats:
        out += '\nh5. IO Statistics\n'
        out += '{{stat key:%(prockey)s.io_read_count,%(prockey)s.io_write_mbytes,%(prockey)s.nr_file_descriptors width:%(width)s height:%(height)s}}<br><br>' % _data
    if memstats:
        out += '\nh5. Memory Statistics\n'
        out += '{{stat key:%(prockey)s.mem_rss,%(prockey)s.mem_vms width:%(width)s height:%(height)s}}<br><br>' % _data
    if threadingstats:
        out += '\nh5. Threading Statistics\n'
        out += '{{stat key:%(prockey)s.nr_threads,%(prockey)s.nr_threads width:%(width)s height:%(height)s}}<br><br>' % _data

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
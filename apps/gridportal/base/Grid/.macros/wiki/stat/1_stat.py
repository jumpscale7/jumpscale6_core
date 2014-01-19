
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc

    stattype = args.getTag('stattype')
    id = args.getTag('id')
    nid = args.getTag('nid')
    actor=j.apps.system.gridmanager
    key = args.getTag('key')
    width = args.getTag('width', 800)
    height = args.getTag('height', 400)
    nic = args.getTag('nic')


    _data = {'nid': nid, 'height':height, 'width':width, 'nic': nic}

    if stattype == 'node':
        cpustats = args.tags.labelExists("cpustats")
        netstats = args.tags.labelExists("netstats")
        memstats = args.tags.labelExists("memstats")

        out = ''

        if cpustats:
            out += '\nh3. CPU Statistics\n'
            out += '|| || ||\n'
            
            out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.cpu.percent&title=CPU Percent&_png=1&width=%(width)s&height=%(height)s&.png!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.cpu.time.system,n%(nid)s.system.cpu.time.user,n%(nid)s.system.cpu.time.iowait,n%(nid)s.system.cpu.time.idle&title=CPU Time&_png=1&width=%(width)s&height=%(height)s&.png!|\n' % _data
        if memstats:
            out += '\nh3. Memory Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.memory.free,n%(nid)s.system.memory.percent,n%(nid)s.system.memory.used&width=%(width)s&height=%(height)s!<br><br>' % _data
        if netstats:
            out += '\nh3. Network Statistics\n'
            out += '|| || ||\n'
            
            out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.network.kbytes.recv,n%(nid)s.system.network.kbytes.send&title=KBytes&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.network.packets.recv,n%(nid)s.system.network.packets.send&title=Packets&width=%(width)s&height=%(height)s!|\n' % _data

            out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.network.drop.in,n%(nid)s.system.network.drop.out&title=Drop&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.system.network.error.in,n%(nid)s.system.network.error.out&title=Error&width=%(width)s&height=%(height)s!|\n' % _data
    
    elif stattype == 'process':
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
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=%(prockey)s.cpu_percent&width=%(width)s&height=%(height)s!<br><br>' % _data
        if iostats:
            out += '\nh5. IO Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=%(prockey)s.io_read_count,%(prockey)s.io_write_mbytes,%(prockey)s.nr_file_descriptors&width=%(width)s&height=%(height)s!<br><br>' % _data
        if memstats:
            out += '\nh5. Memory Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=%(prockey)s.mem_rss,%(prockey)s.mem_vms&width=%(width)s&height=%(height)s!<br><br>' % _data
        if threadingstats:
            out += '\nh5. Threading Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=%(prockey)s.nr_threads,%(prockey)s.nr_threads&width=%(width)s&height=%(height)s!<br><br>' % _data

    elif stattype == 'nic':
        out = ''
        out += '\nh3. Network Interface Statistics\n'
        out += '|| || ||\n'
        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.nic.%(nic)s.kbytes_recv,n%(nid)s.nic.%(nic)s.kbytes_sent&title=KBytes&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.nic.%(nic)s.packets_recv,n%(nid)s.nic.%(nic)s.packets_sent&title=Packets&width=%(width)s&height=%(height)s!|\n' % _data

        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.nic.%(nic)s.dropin,n%(nid)s.nic.%(nic)s.dropout&title=Drop&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.nic.%(nic)s.errin,n%(nid)s.nic.%(nic)s.errout&title=Error&width=%(width)s&height=%(height)s!|\n' % _data
    elif stattype == 'disk':
        obj = actor.getDisks(id=id)
        if not obj:
            out = 'No disk with id %s found' % id
            params.result = (out, doc)
            return params
        obj = obj[0]
        name = obj['path'].replace('/dev/', '')
        diskkey = 'n%s.disk.%s' % (obj['nid'], name)
        _data['diskkey'] = diskkey
        out = ''
        out += '\nh3. Disk Statistics\n'
        out += '|| || ||\n'
        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=%(diskkey)s.space_free_mb,%(diskkey)s.space_used_mb&title=Used Space&width=%(width)s&height=%(height)s&graphType=pie!|!/restmachine/system/gridmanager/getStatImage?statKey=%(diskkey)s.kbytes_read,%(diskkey)s.kbytes_write&title=IO&width=%(width)s&height=%(height)s!|\n' % _data

    else:
        out = '!/restmachine/system/gridmanager/getStatImage?statKey=%s&width=%s&height=%s!'%(key,width,height)
    
    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

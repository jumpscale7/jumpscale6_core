
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc

    stattype = args.getTag('stattype')
    id = args.getTag('id')
    nid = args.getTag('nid')
    key = args.getTag('key')
    width = args.getTag('width', 800)
    height = args.getTag('height', 400)
    iid = args.getTag('iid')
    did = args.getTag('did')
    if did:
        did = did.split('_')[-1]


    _data = {'nid': nid, 'height':height, 'width':width, 'iid': iid, 'did': did}

    if stattype == 'node':
        cpustats = args.tags.labelExists("cpustats")
        netstats = args.tags.labelExists("netstats")
        memstats = args.tags.labelExists("memstats")

        out = ''

        if cpustats:
            out += '\nh3. CPU Statistics\n'
            out += '|| || ||\n'
            
            out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.cpu.percent.avg&title=Average CPU Percent&_png=1&width=%(width)s&height=%(height)s&.png!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.cpu.time.system.avg,n%(nid)s.cpu.time.user.avg,n%(nid)s.cpu.time.iowait.avg,n%(nid)s.cpu.time.idle.avg&title=CPU Time&_png=1&width=%(width)s&height=%(height)s&.png!|\n' % _data
        if memstats:
            out += '\nh3. Memory Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.memory.free.avg,n%(nid)s.memory.percent.avg,n%(nid)s.memory.used.avg&width=%(width)s&height=%(height)s!<br><br>' % _data
        if netstats:
            out += '\nh3. Network Statistics\n'
            out += '|| || ||\n'
            
            out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.network.kbytes.recv.avg,n%(nid)s.network.kbytes.send.avg&title=KBytes&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.network.packets.recv.avg,n%(nid)s.network.packets.send.avg&title=Packets&width=%(width)s&height=%(height)s!|\n' % _data

            out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.network.drop.in.avg,n%(nid)s.network.drop.out.avg&title=Drop&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.network.error.in.avg,n%(nid)s.network.error.out.avg&title=Error&width=%(width)s&height=%(height)s!|\n' % _data
    
    elif stattype == 'process':
        cpustats = args.tags.labelExists("cpustats")
        iostats = args.tags.labelExists("iostats")
        memstats = args.tags.labelExists("memstats")
        threadingstats = args.tags.labelExists("threadingstats")
        
        out = ''
        actor=j.apps.system.gridmanager
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
        
        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.i%(iid)s.network.kbytes.recv.avg,n%(nid)s.i%(iid)s.network.kbytes.send.avg&title=KBytes&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.i%(iid)s.network.packets.recv.avg,n%(nid)s.i%(iid)s.network.packets.send.avg&title=Packets&width=%(width)s&height=%(height)s!|\n' % _data

        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.i%(iid)s.network.drop.in.avg,n%(nid)s.i%(iid)s.network.drop.out.avg&title=Drop&width=%(width)s&height=%(height)s!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.i%(iid)s.network.error.in.avg,i%(iid)s.network.error.out.avg&title=Error&width=%(width)s&height=%(height)s!|\n' % _data
    elif stattype == 'disk':
        out = ''
        out += '\nh3. Disk Statistics\n'
        out += '|| || ||\n'
        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.disk.%(did)s.space.free.last,n%(nid)s.d%(did)s.space.used.last&title=Used Space&width=%(width)s&height=%(height)s&graphType=pie!|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.disk.%(did)s.mbytes.read.avg,n%(nid)s.d%(did)s.mbytes.write.avg&title=IO&width=%(width)s&height=%(height)s!|\n' % _data


    else:
        out = '!/restmachine/system/gridmanager/getStatImage?statKey=%s&width=%s&height=%s!'%(key,width,height)
    
    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

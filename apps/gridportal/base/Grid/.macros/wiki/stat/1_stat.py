
def main(j, args, params, tags, tasklet):
    import urllib
    params.merge(args)

    doc = params.doc

    p=args.tags.getDict()

    stattype = p['stattype'] if p.get('stattype') and not p['stattype'].startswith('$$') else None
    pid = p['pid'] if p.get('pid') and not p['pid'].startswith('$$') else None
    nid = p['nid'] if p.get('nid') and not p['nid'].startswith('$$') else None
    width = p['width'] if p.get('width') and not p['width'].startswith('$$') else 800
    height = p['height'] if p.get('height') and not p['height'].startswith('$$') else 400
    iid = p['iid'] if p.get('iid') and not p['iid'].startswith('$$') else None
    dis = p['did'] if p.get('did') and not p['did'].startswith('$$') else None

    query = list()
    query.append(('height', height))
    query.append(('width', width))

    _data = {'nid': nid, 'pid':pid, 'height':height, 'width':width, 'iid': iid}

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

        if cpustats:
            out += '\nh5. CPU Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.p%(pid)s.cpu_percent_total.avg,n%(nid)s.p%(pid)s.cpu_time_system_total.avg&width=%(width)s&height=%(height)s!<br><br>' % _data
        if iostats:
            out += '\nh5. IO Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.p%(pid)s.io_read_count.avg,n%(nid)s.p%(pid)s.io_write_bytes_total.avg,n%(nid)s.p%(pid)s.nr_file_descriptors_total.avg&width=%(width)s&height=%(height)s!<br><br>' % _data
        if memstats:
            out += '\nh5. Memory Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.p%(pid)s.mem_rss_total.max,n%(nid)s.p%(pid)s.mem_vms_total.last&width=%(width)s&height=%(height)s!<br><br>' % _data
        if threadingstats:
            out += '\nh5. Threading Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.p%(pid)s.nr_threads_total.max,n%(nid)s.p%(pid)s.nr_threads_total.last&width=%(width)s&height=%(height)s!<br><br>' % _data

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
        out += '|!/restmachine/system/gridmanager/getStatImage?statKey=n%(nid)s.d%(did)s.space.free.last,n%(nid)s.d%(did)s.space.used.last&title=Used Space&width=%(width)s&height=%(height)s&graphType=pie!||\n' % _data


    else:
        out = '!/restmachine/system/gridmanager/getStatImage?statKey=%s&width=%s&height=%s!'%(p["key"],p["width"],p["height"])
    
    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

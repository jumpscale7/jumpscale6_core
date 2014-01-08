
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags

    p=args.tags.getDict()

    stattype = p['stattype'] if p.get('stattype') and not p['stattype'].startswith('$$') else None
    pid = p['pid'] if p.get('pid') and not p['pid'].startswith('$$') else None
    nid = p['nid'] if p.get('nid') and not p['nid'].startswith('$$') else None
    width = p['width'] if p.get('width') and not p['width'].startswith('$$') else 800
    height = p['height'] if p.get('height') and not p['height'].startswith('$$') else 400

    if stattype == 'node':
        out='!/restmachine/system/gridmanager/getStatImage?statKey=%s&_png=1&width=%s&height=%s&.png!'%(p["key"],p["width"],p["height"])
    elif stattype == 'process':
        cpustats = args.tags.labelExists("cpustats")
        iostats = args.tags.labelExists("iostats")
        memstats = args.tags.labelExists("memstats")
        threadingstats = args.tags.labelExists("threadingstats")
        
        out = ''

        if cpustats:
            out += '\nh5. CPU Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%s.p%s.cpu_percent_total.avg,n%s.p%s.cpu_time_system_total.avg&_png=1&width=%s&height=%s&.png!<br><br>' % (nid, pid, nid, pid, width, height)
        if iostats:
            out += '\nh5. IO Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%s.p%s.io_read_count.avg,n%s.p%s.io_write_bytes_total.avg,n%s.p%s.nr_file_descriptors_total.avg&_png=1&width=%s&height=%s&.png!<br><br>' % (nid, pid, nid, pid, nid, pid, width, height)
        if memstats:
            out += '\nh5. Memory Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%s.p%s.mem_rss_total.max,n%s.p%s.mem_vms_total.last&_png=1&width=%s&height=%s&.png!<br><br>' % (nid, pid, nid, pid, width, height)
        if threadingstats:
            out += '\nh5. Threading Statistics\n'
            out += '!/restmachine/system/gridmanager/getStatImage?statKey=n%s.p%s.nr_threads_total.max,n%s.p%s.nr_threads_total.last&_png=1&width=%s&height=%s&.png!<br><br>' % (nid, pid, nid, pid, width, height)

    else:
        out = '!/restmachine/system/gridmanager/getStatImage?statKey=%s&_png=1&width=%s&height=%s&.png!'%(p["key"],p["width"],p["height"])
    
    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

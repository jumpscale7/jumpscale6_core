import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system","gridmanager")
    #this makes sure bootstrap datatables functionality is used
    out="{{datatables_use}}\n\n"

    fields = ['name', 'ipaddr', 'mac', 'lastcheck']

    out+="||Name||IP Address||MAC Address||Last Checked||\n"

    nid = args.tags.getDict().get("nid") if not args.tags.getDict().get("nid", "").startswith('$$') else None

    nics = actor.getNics(nid=nid,size=2000)
    if not nics:
        params.result = ('No NICs found', doc)
        return params

    for nic in nics:
        for field in fields:
            if field == 'lastcheck':
                data = datetime.datetime.fromtimestamp(nic[field]).strftime('%m-%d %H:%M:%S') or ''
            elif field == 'name':
                data = '[%(name)s|/grid/nic?id=%(guid)s&nic=%(name)s&nid=%(nid)s]' %  nic
            elif isinstance(nic[field], list):
                data = ', '.join(nic[field])
            else:
                data = str(nic[field]).replace('[', '&#91;') #Some messages had square brackets
            out += "|%s" % data
        out += "|"
        out += "\n"

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

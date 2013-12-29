
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters:True}}}}\n")

    #[u'otherid', u'description', u'roles', u'mem', u'netaddr', u'ipaddr', u'nid', u'lastcheck', u'state', u'gid', u'active', u'cpucore', u'type', u'id', u'name']
    fields = ['organization', 'name', 'category', 'descr']

    out.append('||organization||name||category||description||')

    for jscript in actor.getJumpscripts():
        line = [""]

        for i in range(0, len(fields)):
            # add links
            if i == 1:
                line.append('[%s|/grid/jumpscript?jsorganization=%s&jsname=%s]' % (jscript[1], jscript[0], jscript[1]))
            else:
                text = jscript[i].replace('\n', '')
                line.append(str(text))

        line.append("")
        out.append("|".join(line))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

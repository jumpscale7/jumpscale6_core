import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.tags.getDict().get('id', None)

    obj = actor.getJobs(id=id)
    if not obj:
        params.result = ('Job not found')
        return params

    obj = obj[0]

    out = ['||Property||Value||']

    fields = ['id', 'lock', 'timeStop', 'lockduration', 'result', 'category', 'jsname', 'children', 'source', 'state', 'gid', 'childrenActive', 'jscriptid', 'description', 'parent', 'args', 'sessionid', 'jsorganization', 'roles', 'timeStart', 'timeout', 'resultcode']

    for field in fields:
        if field in ('children'):
            out.append("|%s|%s|" % (field.capitalize(), ', '.join(obj[field])))
        elif field == 'timeStart':
            timeStart = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), timeStart))
        elif field in ('args', 'childrenActive'):
            data = ''
            if obj[field]:
                import JumpScale.baselib.serializers
                obj[field] = j.db.serializers.ujson.loads(obj[field])
            for k, v in obj[field].iteritems():
                data += "%s:%s, " % (k,v)
            out.append("|%s|%s|" % (field.capitalize(), data[0:-2]))
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

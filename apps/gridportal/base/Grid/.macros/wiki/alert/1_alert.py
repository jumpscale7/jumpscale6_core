import JumpScale.grid.osis

def main(j, args, params, tags, tasklet):
    guid = args.getTag('guid')
    if not guid:
        out = 'Missing alert param "id"'
        params.result = (out, args.doc)
        return params            

    syscl = j.core.osis.getClientForNamespace('system')
    alert = syscl.alert.get(guid)
    alert = alert.dump()

    if alert==None:
        params.result = ('Alert with guid %s not found' % guid, args.doc)
        return params

    color = 'green' if alert['state'] == 'OK' else ('red' if alert['state'] == 'ERROR' else 'orange')
    alert['state'] = '{color:%s}%s{color}' % (color, alert['state'])

    args.doc.applyTemplate(alert)

    params.result = (args.doc, args.doc)
    return params
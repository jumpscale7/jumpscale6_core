import datetime

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing alert id param "id"'
        params.result = (out, args.doc)
        return params

    alert = j.apps.system.gridmanager.getAlerts(id=id)
    if not alert:
        params.result = ('Alert with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = alert[0]
        for attr in ['lasttime', 'inittime', 'closetime']:
            obj[attr] = datetime.datetime.fromtimestamp(obj[attr]).strftime('%Y-%m-%d %H:%M:%S')
        obj['errorconditions'] = ', '.join([str(x) for x in obj['errorconditions']])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


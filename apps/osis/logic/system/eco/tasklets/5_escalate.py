def main(j, params, service, tags, tasklet):
    """
    Create or update Alert object
    """

    import time
    eco = params.value
    session = params.session
    alertservice = j.core.osis.cmds._getOsisInstanceForCat('system', 'alert')

    alerts = alertservice.search({'eco':eco['guid']}, session=session)[1:]
    alert = {'eco': eco['guid'],
                'errormessage': eco['errormessage'],
                'errormessagePub': eco['errormessagePub'],
                'category': eco['category'],
                'gid': eco['gid'],
                'nid': eco['nid'],
                'lasttime': eco['lasttime']}
    if not alerts:
        alert['inittime'] = eco['epoch']
        alert['state'] = 'ALERT'
        alert['level'] = 1
        alertobj = alertservice.new()
        alertobj.load(alert)
        alert = alertobj.dump()

    else:
        alertdata = alerts[0]
        if alertdata['state'] in ['RESOLVED', 'CLOSED']:
            alertdata['state'] = 'ALERT'
        alertdata.update(alert)
        alert = alertdata
    alertservice.set(None, alert, session=session)
    
def match(j, params, service, tags, tasklet):
    return params.action == 'set'

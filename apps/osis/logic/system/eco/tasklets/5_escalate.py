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
                'lasttime': eco['epoch']}
    if not alerts:
        alert['inittime'] = eco['epoch']
        alert['description'] = eco['description']
        alert['state'] = 'ALERT'
        alert['descriptionpub'] = eco['descriptionpub']
    else:
        alertdata = alerts[0]
        if alertdata['state'] in ['RESOLVED', 'CLOSED']:
            alertdata['state'] = 'ALERT'
        alertdata.update(alert)		
        alert = alertdata
    alertservice.set(alert, session=session)
    
def match(j, params, service, tags, tasklet):
    return params.action == 'set'
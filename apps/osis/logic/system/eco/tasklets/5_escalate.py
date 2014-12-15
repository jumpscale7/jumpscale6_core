BREACHTIME = 3600

def main(j, params, service, tags, tasklet):
    import time
    eco = params.value
    session = params.session
    now = time.time()

    def raiseEvent():
        eco['lastalert'] = now
        print eco

    if eco['state'] in ('NEW', 'ALERT'):
        eco['state'] = 'ALERT'
        if service.exists(eco['guid'], session=session):
            ecodb = service.get(eco['guid'], session=session)
            if ecodb['state'] == 'ALERT':
                if ecodb['lastalert'] + BREACHTIME > now:
                    eco['slabreach'] = ecodb.get('slabreach', 0) + 1
                    raiseEvent()
            else:
                raiseEvent()
        else:
            raiseEvent()

def match(j, params, service, tags, tasklet):
    return params.action == 'set'
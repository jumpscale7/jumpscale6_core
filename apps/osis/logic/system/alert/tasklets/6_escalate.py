
def main(j, params, service, tags, tasklet):
    """
    Create or update Alert object
    """
    alert = params.value
    alerts_queue = j.clients.redis.getByInstanceName('system').getQueue('alerts')
    if alert['state'] == 'ALERT':
        alerts_queue.put(alert)

def match(j, params, service, tags, tasklet):
    return params.action == 'set'
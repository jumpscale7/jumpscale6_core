
def main(j, args, params, tags, tasklet):
    import gevent
    gevent.hub.MAIN.throw(SystemExit(3))

def match(j, args, params, tags, tasklet):
    return True

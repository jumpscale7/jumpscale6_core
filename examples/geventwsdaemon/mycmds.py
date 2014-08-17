class MyCommands(object):

    def __init__(self, daemon):
        self.daemon = daemon

    def ping(self, session):
        return 'pong'

    def echo(self, arg, session):
        return arg

    def wait(self, org, user,session):
        print "wait:%s" % user
        key = "%s_%s" % (org, user)
        while not self.work.has_key(key):
            time.sleep(1)
        return self.work[key]

    def scheduleJob(self, org, user, job,session):
        key = "%s_%s" % (org, user)
        self.work[key] = 1

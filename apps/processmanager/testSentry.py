from JumpScale import j

j.application.start("reload")

from raven import Client
client = Client('http://18275531e40849ae8f259a4edd8f1c22:d43b0396addb4b789cd6c325a9ceb36e@127.0.0.1:9000/2')


try:
    print "1"
    1/0
except:
    client.captureException()


j.application.stop()
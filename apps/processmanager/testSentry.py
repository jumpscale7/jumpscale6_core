from JumpScale import j

j.application.start("reload")




from raven import Client
client = Client('http://18275531e40849ae8f259a4edd8f1c22:d43b0396addb4b789cd6c325a9ceb36e@localhost:9000/2')

try:
    print "1"
    1/0
except:
    # from raven.utils.stacks import *
    # frames=iter_stack_frames()
    # frames=iter_traceback_frames(tb)
    # get_stack_info(frames)
    # from IPython import embed
    # print "DEBUG NOW opop"
    # embed()

    client.captureException()


j.application.stop()
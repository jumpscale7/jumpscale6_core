from JumpScale import j

descr = """
some actions doing tests
"""

#optional info
organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"

import time

@queue("default")
@log(5)
@nojob()
def log(self):
    """
    this is a logging function not doing anything but logging
    the @log makes sure all happening gets logged to the job & central logging system, std logging is off !!!
    the @nojob means will not create a job object when executing this action
    """
    j.logger.log(logmsg, level=5, category="test_category")

@queue("io")
def error(self):
    """
    this error will be done in queue io
    """
    return 5/0

@recurring(60)
@queue("io")
@nojo
def msg_scheduled():
    """
    this will print a message each 60 seconds on worker queue io
    """
    msg="alive"
    print msg

@timeout(10)
def wait(ttime=5):
    """
    this will fail when ttime>10
    """
    time.sleep(ttime)

@debug
def error(self):
    """
    be careful when debugging because will be done in mother process of agent, DO NEVER DO THIS IN PRODUCTION
    """
    from IPython import embed
    print "DEBUG NOW"
    embed()
    




from JumpScale import j

descr = """
critical alert
"""

organization = "jumpscale"
enable = True

def escalateL1(watchdogevent):
    print "escalateL1"
    return
    from IPython import embed
    print "DEBUG NOW watchdogevent 1"
    embed()

def escalateL2(watchdogevent):    
    from IPython import embed
    print "DEBUG NOW watchdogevent 2"
    embed()
    
def escalateL3(watchdogevent):    
    from IPython import embed
    print "DEBUG NOW watchdogevent 3"
    embed()

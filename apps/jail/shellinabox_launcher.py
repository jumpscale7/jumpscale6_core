
import os
# os.system(command)
import sys
import time
args=sys.argv
import ujson as json
import psutil

from IPython import embed
print "DEBUG NOW oo"
embed()


from urlparse import urlparse, parse_qs

example="http://$server?user=auser&session=mysession&secret=1234&cmd='ls /opt'"

o=urlparse(args[1])
    
args=parse_qs(o.query)

args2={}
for key,val in args.iteritems():
    val=val[0]
    args2[key]=val

if not args2.has_key("user") or not args2.has_key("session") or not args2.has_key("secret"):
    print "please make sure your request is in form as example shown:"
    print example
    print "cmd is optional."
    sys.exit()

args={}

user=args2["user"]

class Session():
    def __init__(self):
        self.epoch=int(time.time())
        self.pids=[]
        self.addPid(os.getpid())

    def addPid(self,pid):
        if pid not in self.pids:
            self.pids.append(pid)

import redis
r = redis.StrictRedis(host='localhost', port=7768)

name="%s__%s"%(args2["user"],args2["session"])

if r.hexists("robot:sessions", name):
    sessiondict=json.loads(r.hget("robot:sessions", name))
    session=Session()
    session.__dict__.update(sessiondict)
    session.addPid(os.getpid())
    po=psutil.Process(os.getpid())    
    session.addPid(po.parent.pid) #need to remove parent as well                     

else:
    session=Session()

homepath="/home/%s"%args2["user"]
secrpath="%s/.secret"%homepath

if not os.path.isdir(homepath):
    print "ERROR: could not find user on system."
    print homepath
    sys.exit()

if not os.path.isfile(secrpath):
    print "ERROR: could not find user on system, secret was not defined."
    sys.exit()

file = open(secrpath, 'r')
secret=file.read().strip()

if args2["secret"]<>secret:
    print "ERROR: secret not correct."
    sys.exit()
  
r.hset("robot:sessions", name, json.dumps(session.__dict__))

# _stderr = sys.stderr
# _stdout = sys.stdout

# null = open(os.devnull,'wb')
# sys.stdout = null
# sys.stderr = null

# os.system("tmux kill-session -t %s"%name)
# os.system("tmux new-session -d -s %s  js"%name)
# os.system("tmux set-option -t %s status off"%name)
# os.system("tmux send -t %s clear ENTER"%name)

# sys.stderr=_stderr
# sys.stdout=_stdout

# print "Start Robot Session"

# print r.hget("robot:sessions", name)

cmd="sudo -P -u %s tmux a -t %s"%(user,user)
print cmd
os.system(cmd)

# os.system("tmux send -t %s  exit  ENTER"%name)


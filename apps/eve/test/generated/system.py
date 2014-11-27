from mongoengine import *

classes=[]
class system_audit(Document):
    id = IntField(required=True)
    user = StringField(required=True)
    result = StringField(required=True)
    call = StringField(required=True)
    statuscode = StringField(required=True)
    args = StringField(required=True)
    kwargs = StringField(required=True)
    timestamp = StringField(required=True)
classes.append(system_audit)

class system_info(Document):
    nid = IntField(required=True)
    gid = IntField(required=True)
    category = StringField(required=True)
    content = StringField(required=True)
    epoch = IntField(required=True)
    id = IntField(required=True,help_text='Auto generated id @optional')
classes.append(system_info)

class system_group(Document):
    id = IntField(required=True)
    domain = StringField(required=True)
    gid = IntField(required=True)
    roles =  ListField(StringField(), default=list,)
    active = BooleanField(required=True)
    description = StringField(required=True)
    lastcheck = IntField(required=True,help_text=' epoch of last time the info updated')
    users =  ListField(StringField(), default=list,)
classes.append(system_group)

class system_jumpscript(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    name = StringField(required=True)
    descr = StringField(required=True)
    category = StringField(required=True)
    organization = StringField(required=True)
    author = StringField(required=True)
    license = StringField(required=True)
    version = StringField(required=True)
    roles =  ListField(StringField(), default=list,)
    action = StringField(required=True)
    source = StringField(required=True)
    path = StringField(required=True)
    args =  ListField(StringField(), default=list,)
    enabled = BooleanField(required=True)
    async = BooleanField(required=True)
    period = IntField(required=True)
    order = IntField(required=True)
    queue = StringField(required=True)
    log = BooleanField(required=True)
classes.append(system_jumpscript)

class system_eco(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    aid = IntField(required=True)
    pid = IntField(required=True)
    jid = IntField(required=True)
    masterjid = IntField(required=True)
    epoch = IntField(required=True,help_text=' epoch')
    appname = StringField(required=True)
    level = IntField(required=True,help_text=' 1:critical, 2:warning, 3:info')
    type = StringField(required=True)
    state = StringField(required=True,help_text=' ["NEW","ALERT","CLOSED"]')
    errormessage = StringField(required=True)
    errormessagepub = StringField(required=True)
    category = StringField(required=True,help_text=' dot notation e.g. machine.start.failed')
    tags = StringField(required=True,help_text=' e.g. machine:2323')
    code = StringField(required=True)
    funcname = StringField(required=True)
    funcfilename = StringField(required=True)
    funclinenr = IntField(required=True)
    backtrace = StringField(required=True)
    backtracedetailed = StringField(required=True)
    extra = StringField(required=True)
    lasttime = IntField(required=True,help_text=' last time there was an error condition linked to this alert')
    closetime = IntField(required=True,help_text=' alert is closed, no longer active')
    occurrences = IntField(required=True,help_text=' nr of times this error condition happened')
classes.append(system_eco)

class system_nic(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    name = StringField(required=True)
    mac = StringField(required=True)
    ipaddr =  ListField(StringField(), default=list,)
    active = BooleanField(required=True)
    lastcheck = IntField(required=True,help_text=' epoch of last time the info was checked from reality')
classes.append(system_nic)

class system_node(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    name = StringField(required=True)
    roles =  ListField(StringField(), default=list,)
    netaddr = StringField(required=True)
    machineguid = StringField(required=True)
    ipaddr =  ListField(StringField(), default=list,)
    active = BooleanField(required=True)
    peer_stats = IntField(required=True,help_text=' node which has stats for this node')
    peer_log = IntField(required=True,help_text=' node which has transactionlog or other logs for this node')
    peer_backup = IntField(required=True,help_text=' node which has backups for this node')
    description = StringField(required=True)
    lastcheck = IntField(required=True)
    _meta =  ListField(StringField(), default=list,help_text=' osisrootobj,$namespace,$category,$version')
classes.append(system_node)

class system_alert(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    description = StringField(required=True)
    descriptionpub = StringField(required=True)
    level = IntField(required=True,help_text=' 1:critical, 2:warning, 3:info')
    category = StringField(required=True,help_text=' dot notation e.g. machine.start.failed')
    tags = StringField(required=True,help_text=' e.g. machine:2323')
    state = StringField(required=True,help_text=' ["NEW","ALERT","CLOSED"]')
    inittime = IntField(required=True,help_text=' first time there was an error condition linked to this alert')
    lasttime = IntField(required=True,help_text=' last time there was an error condition linked to this alert')
    closetime = IntField(required=True,help_text=' alert is closed, no longer active')
    nrerrorconditions = IntField(required=True,help_text=' nr of times this error condition happened')
    errorconditions =  ListField(IntField(), default=list,help_text=' ids of errorconditions')
classes.append(system_alert)

class system_machine(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    name = StringField(required=True)
    roles =  ListField(StringField(), default=list,)
    netaddr = StringField(required=True)
    ipaddr =  ListField(StringField(), default=list,)
    active = BooleanField(required=True)
    state = StringField(required=True,help_text=' STARTED,STOPPED,RUNNING,FROZEN,CONFIGURED,DELETED')
    mem = IntField(required=True,help_text=' in MB')
    cpucore = IntField(required=True)
    description = StringField(required=True)
    otherid = StringField(required=True)
    type = StringField(required=True,help_text=' VM,LXC')
    lastcheck = IntField(required=True,help_text=' epoch of last time the info was checked from reality')
classes.append(system_machine)

class system_process(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    jpdomain = StringField(required=True)
    jpname = StringField(required=True)
    pname = StringField(required=True,help_text=' process name')
    sname = StringField(required=True,help_text=' name as specified in startup manager')
    ports =  ListField(IntField(), default=list,)
    instance = StringField(required=True)
    systempid =  ListField(IntField(), default=list,help_text=' system process id (PID) at this point')
    epochstart = IntField(required=True)
    epochstop = IntField(required=True)
    active = BooleanField(required=True)
    lastcheck = IntField(required=True)
    cmd = StringField(required=True)
    workingdir = StringField(required=True)
    parent = StringField(required=True)
    type = StringField(required=True)
    statkey = StringField(required=True)
    nr_file_descriptors = FloatField(required=True)
    nr_ctx_switches_voluntary = FloatField(required=True)
    nr_ctx_switches_involuntary = FloatField(required=True)
    nr_threads = FloatField(required=True)
    cpu_time_user = FloatField(required=True)
    cpu_time_system = FloatField(required=True)
    cpu_percent = FloatField(required=True)
    mem_vms = FloatField(required=True)
    mem_rss = FloatField(required=True)
    io_read_count = FloatField(required=True)
    io_write_count = FloatField(required=True)
    io_read_bytes = FloatField(required=True)
    io_write_bytes = FloatField(required=True)
    nr_connections_in = FloatField(required=True)
    nr_connections_out = FloatField(required=True)
classes.append(system_process)

class system_grid(Document):
    id = IntField(required=True)
    name = StringField(required=True)
    useavahi = BooleanField(required=True)
    nid = IntField(required=True)
classes.append(system_grid)

class system_user(Document):
    id = IntField(required=True)
    domain = StringField(required=True)
    gid = IntField(required=True)
    passwd = StringField(required=True)
    roles =  ListField(StringField(), default=list,)
    active = BooleanField(required=True)
    description = StringField(required=True)
    emails =  ListField(StringField(), default=list,)
    xmpp =  ListField(StringField(), default=list,)
    mobile =  ListField(StringField(), default=list,)
    lastcheck = IntField(required=True)
    groups =  ListField(StringField(), default=list,)
    authkey = StringField(required=True)
    data = StringField(required=True)
    authkeys =  ListField(StringField(), default=list,)
classes.append(system_user)

class system_test(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    name = StringField(required=True)
    testrun = StringField(required=True)
    path = StringField(required=True)
    state = StringField(required=True)
    priority = IntField(required=True)
    organization = StringField(required=True)
    author = StringField(required=True)
    version = IntField(required=True)
    categories =  ListField(StringField(), default=list,)
    starttime = IntField(required=True)
    endtime = IntField(required=True)
    enable = BooleanField(required=True)
    result =  ListField(field=StringField(), default=list,)
    output =  ListField(field=StringField(), default=list,)
    eco =  ListField(field=StringField(), default=list,)
    license = StringField(required=True)
    source =  ListField(field=StringField(), default=list,)
classes.append(system_test)

class system_heartbeat(Document):
    nid = IntField(required=True)
    gid = IntField(required=True)
    lastcheck = IntField(required=True)
    id = IntField(required=True,help_text='Auto generated id @optional')
classes.append(system_heartbeat)

class system_disk(Document):
    id = IntField(required=True)
    partnr = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    path = StringField(required=True)
    size = IntField(required=True)
    free = IntField(required=True)
    ssd = IntField(required=True)
    fs = StringField(required=True)
    mounted = BooleanField(required=True)
    mountpoint = StringField(required=True)
    active = BooleanField(required=True)
    model = StringField(required=True)
    description = StringField(required=True)
    type =  ListField(StringField(), default=list,help_text=' BOOT, DATA, ...')
    lastcheck = StringField(required=True,help_text=' epoch of last time the info was checked from reality')
classes.append(system_disk)

class system_vdisk(Document):
    id = IntField(required=True)
    gid = IntField(required=True)
    nid = IntField(required=True)
    path = StringField(required=True)
    backingpath = StringField(required=True)
    size = IntField(required=True)
    free = IntField(required=True)
    sizeondisk = IntField(required=True)
    fs = StringField(required=True)
    active = BooleanField(required=True)
    description = StringField(required=True)
    role = StringField(required=True)
    machineid = IntField(required=True)
    order = IntField(required=True)
    type = StringField(required=True)
    backup = BooleanField(required=True)
    backuptime = IntField(required=True)
    expiration = IntField(required=True)
    backuplocation = StringField(required=True)
    devicename = StringField(required=True)
    lastcheck = IntField(required=True)
classes.append(system_vdisk)

[actor] @dbtype:mem,fs
    """
    gateway to grid
    """    
    method:getProcessStats
        """     
        ask the right processmanager on right node to get the information
        """
        var:nodeId int,,id of node 
        var:domain str,,optional domain name for process @tags: optional
        var:name str,,optional name for process @tags: optional
        result:json

    method:getProcessesActive
        """     
        ask the right processmanager on right node to get the info (this comes not from osis)
        output all relevant info (no stat info for that we have getProcessStats)
        """
        var:nodeId int,,id of node (if not specified goes to all nodes and aggregates) @tags: optional
        var:name str,,optional name for process name (part of process name) @tags: optional
        var:domain str,,optional name for process domain (part of process domain) @tags: optional
        result:json

    method:getJob
        """
        gets relevant info of job (also logs)
        can be used toreal time return job info
        """
        var:id str,,obliged id of job
        var:includeloginfo bool,True,if true fetch all logs of job & return as well @tags: optional
        var:includechildren bool,True,if true look for jobs which are children & return that info as well @tags: optional

    method:getNodeSystemStats
        """     
        ask the right processmanager on right node to get the information about node system
        """
        var:nodeId int,,id of node
        result:json

    method:getStatImage
        """     
        get png image as binary format
        comes from right processmanager
        """
        var:statKey str,,e.g. n1.disk.mbytes.read.sda1.last
        var:width int,500, @tags: optional
        var:height int,200, @tags: optional
        result:binary

    method:getNodes
        """     
        list found nodes (comes from osis)
        """
        result:list(list)
        var:gid int,,find logs for specified grid @tags: optional
        var:name str,,match on text in name @tags: optional
        var:roles str,,match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.) @tags: optional
        var:ipaddr str,,comma separated list of ip addr to match against @tags: optional
        var:macaddr str,,comma separated list of mac addr to match against @tags: optional

    method:getLogs
        """     
        interface to get log information
        #result:json array
        """
        var:id str,,only find 1 log entry @tags: optional
        var:level int,,level between 1 & 9; all levels underneath are found e.g. level 9 means all levels @tags: optional
        var:category str,,match on multiple categories; are comma separated @tags: optional
        var:text str,,match on text in body @tags: optional 
        var:from_ str,-1h,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs from date specified  (-4d means 4 days ago) @tags: optional
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs to date specified  @tags: optional
        var:jid int,,find logs for specified jobid @tags: optional
        var:nid int,,find logs for specified node @tags: optional
        var:gid int,,find logs for specified grid @tags: optional
        var:pid int,,find logs for specified process (on grid level) @tags: optional
        var:tags str,,comma separted list of tags/labels @tags: optional

        
    method:getJobs
        """     
        interface to get job information
        #result:json array
        """
        var:id str,,only find 1 job entry @tags: optional
        var:from_ str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs from date specified  (-4d means 4 days ago) @tags: optional
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs to date specified  @tags: optional
        var:nid int,,find jobs for specified node @tags: optional
        var:gid int,,find jobs for specified grid @tags: optional
        var:parent str,,find jobs which are children of specified parent @tags: optional
        var:roles str,,match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.) @tags: optional
        var:state str,,OK;ERROR;... @tags: optional
        var:jsorganization str,, @tags: optional
        var:jsname str,, @tags: optional


    method:getErrorconditions
        """     
        interface to get errorcondition information (eco)
        #result:json array
        """
        var:id str,,only find 1 eco entry @tags: optional
        var:level int,,level between 1 & 3; all levels underneath are found e.g. level 3 means all levels @tags: optional
        var:descr str,,match on text in descr @tags: optional  
        var:descrpub str,,match on text in descrpub @tags: optional
        var:from_ str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos from date specified  (-4d means 4 days ago) @tags: optional
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos to date specified  @tags: optional
        var:nid int,,find ecos for specified node @tags: optional
        var:gid int,,find ecos for specified grid @tags: optional
        var:category str,,match on multiple categories; are comma separated @tags: optional
        var:tags str,,comma separted list of tags/labels @tags: optional
        var:type str,, v
        var:jid int,,find ecos for specified job @tags: optional
        var:jidparent str,,find ecos which are children of specified parent job @tags: optional        
        var:jsorganization str,,find ecos coming from scripts from this org @tags: optional
        var:jsname str,,find ecos coming from scripts with this name @tags: optional

    method:getProcesses
        """     
        list processes (comes from osis), are the grid unique processes (not integrated with processmanager yet)
        """
        var:id str,,only find 1 process entry @tags: optional
        var:name str,,match on text in name @tags: optional
        var:nid int,,find logs for specified node @tags: optional
        var:gid int,,find logs for specified grid @tags: optional        
        var:aid int,,find logs for specified application type @tags: optional
        var:from_ str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes from date specified  (-4d means 4 days ago) @tags: optional
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes to date specified @tags: optional
        result:list(list)

    method:getApplications
        """     
        list known application types (applicationtype in osis)
        """
        var:id str,,only find 1 application entry @tags: optional
        var:type str,, @tags: optional
        var:descr str,,match on text in descr @tags: optional
        result:list(list)

    method:getGrids
        """     
        list grids
        """
        result:list(list)


    method:getJumpscripts
        """
        calls internally the agentcontroller
        return: lists the jumpscripts with main fields (organization, name, category, descr)
        """
        var:jsorganization str,,find jumpscripts @tags: optional
        
    method:getJumpscript
        """
        calls internally the agentcontroller to fetch detail for 1 jumpscript
        """
        var:jsorganization str,,
        var:jsname str,,

    method:getAgentControllerSessions
        """
        calls internally the agentcontroller
        """ 
        var:roles str,,match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.) @tags: optional
        var:nid int,,find for specified node (on which agents are running which have sessions with the agentcontroller) @tags: optional
        var:active bool,,is session active or not @tags: optional


    method:getAgentControllerActiveJobs
        """
        calls internally the agentcontroller
        list jobs now running on agentcontroller
        """



[actor] @dbtype:mem,fs
    """
    gateway to grid
    """    
    method:getProcessStats
        """     
        ask the right processmanager on right node to get the information
        """
        var:nodeId int,,id of node
        var:domain str,,optional domain name for process
        var:name str,,optional name for process
        result:json

    method:getNodeSystemStats
        """     
        ask the right processmanager on right node to get the information about node system
        """
        var:nodeId int,,id of node
        result:json

    method:getStatImage
        """     
        get png image as binary format
        """
        var:statKey str,,e.g. n1.disk.mbytes.read.sda1.last
        var:width int,,
        var:height int,,
        result:binary

    method:getNodes
        """     
        list found nodes
        """
        result:list(list)
        var:gid int,,find logs for specified grid
        var:name str,,match on text in name
        var:roles str,,match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        var:ipaddr str,,comma separated list of ip addr to match against
        var:macaddr str,,comma separated list of mac addr to match against

    method:getLogs
        """     
        interface to get log information
        #result:json array
        """
        var:id str,,only find 1 log entry
        var:level int,,level between 1 & 9; all levels underneath are found e.g. level 9 means all levels
        var:category str,,match on multiple categories; are comma separated
        var:text str,,match on text in body
        var:from str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs from date specified  (-4d means 4 days ago)
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs to date specified 
        var:jid int,,find logs for specified jobid
        var:nid int,,find logs for specified node
        var:gid int,,find logs for specified grid
        var:pid int,,find logs for specified process (on grid level)
        var:tags str,,comma separted list of tags/labels

        
    method:getJobs
        """     
        interface to get job information
        #result:json array
        """
        var:id str,,only find 1 job entry
        var:from str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs from date specified  (-4d means 4 days ago)
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs to date specified 
        var:nid int,,find jobs for specified node
        var:gid int,,find jobs for specified grid
        var:parent str,,find jobs which are children of specified parent
        var:state str,,OK;ERROR;... @todo complete
        var:jsorganization str,,
        var:jsname str,,


    method:getErrorconditions
        """     
        interface to get errorcondition information (eco)
        #result:json array
        """
        var:id str,,only find 1 eco entry
        var:level int,,level between 1 & 3; all levels underneath are found e.g. level 3 means all levels
        var:descr str,,match on text in descr
        var:descrpub str,,match on text in descrpub
        var:from str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos from date specified  (-4d means 4 days ago)
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos to date specified 
        var:nid int,,find ecos for specified node
        var:gid int,,find ecos for specified grid
        var:category str,,match on multiple categories; are comma separated
        var:tags str,,comma separted list of tags/labels
        var:type str,,
        var:jid int,,find ecos for specified job
        var:jidparent str,,find ecos which are children of specified parent job        
        var:jsorganization str,,find ecos coming from scripts from this org
        var:jsname str,,find ecos coming from scripts with this name

    method:getProcesses
        """     
        list found nodes
        """
        var:id str,,only find 1 process entry
        var:name str,,match on text in name
        var:nid int,,find logs for specified node
        var:gid int,,find logs for specified grid        
        var:aid int,,find logs for specified application type
        var:from str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes from date specified  (-4d means 4 days ago)
        var:to str,,-4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes to date specified 
        result:list(list)

    method:getApplications
        """     
        list found nodes (applicationtype in osis)
        """
        var:id str,,only find 1 process entry
        var:type str,,
        var:descr str,,match on text in descr
        result:list(list)

    method:getGrids
        """     
        list grids
        """
        result:list(list)


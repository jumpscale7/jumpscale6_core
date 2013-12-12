[actor] @dbtype:mem #tasklets
    method: listJobs
        """
        Gets jobs that match criteria
        """
        var:ffrom str,,format -4h, -3d, etc @tags: optional
        var:to str,,format -4h, -3d, etc @tags: optional
        var:nid int,, @tags: optional
        var:gid int,, @tags: optional
        var:parent str,, @tags: optional
        var:state str,, @tags: optional
        var:jsorganization str,, @tags: optional
        var:jsname str,, @tags: optional
        result:dict
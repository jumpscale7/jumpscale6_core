[actor] @dbtype:mem #tasklets
    method: listJobs
        """
        Gets jobs that match criteria
        """
        var:ffrom str,,format -4h, -3d, etc
        var:to str,,format -4h, -3d, etc
        var:nid int,,
        var:gid int,,
        var:parent str,,
        var:state str,,
        var:jsorganization str,,
        var:jsname str,,
        result:dict
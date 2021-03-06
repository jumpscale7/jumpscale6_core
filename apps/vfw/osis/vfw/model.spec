#IS EXAMPLE, COPY  to category

[rootmodel:virtualfirewall] #@index
    prop:id int,,is unique id 
    prop:gid int,,grid on which firewall is running
    prop:nid int,,node on which firewall is running
    prop:name str,,
    prop:descr str,,
    prop:type str,,
    prop:domain str,,free to choose domain e.g. space of customer
    prop:host str,, host ipaddress of the virtual firewall
    prop:username str,, username to manage the virtual firewall
    prop:password str,, password to manage the virtual firewall
    prop:tcpForwardRules list(tcpForwardRule),,set of rules for tcp forwarding; when more than 1 and same source port then tcp loadbalancing
    prop:masquerade bool,True,if True then masquerading done from internal network to external
    prop:wsForwardRules list(wsForwardRule),,set of rules for reverse proxy
    prop:networkid str,,
    prop:internalip str,,
    prop:pubips list(str),,
    prop:version int,2,
    prop:state str,, OK;ERROR;INIT;DELETED
    prop:moddate int,,


[model:tcpForwardRule] #@index
    """
    """
    prop:fromAddr str,,ip addr source
    prop:fromPort str,,tcp port incoming
    prop:toAddr str,,ip addr where to direct to
    prop:toPort str,,tcp port where it is redirected to
    prop:protocol str,,tcp or upd

[model:wsForwardRule] #@index
    prop:url str,,url domain name e.g. www.incubaid.com
    prop:toUrls str,,e.g. [192.168.1.20:3000/test/...]   #so can be port; ip; url part; when more than 1 then loadbalancing


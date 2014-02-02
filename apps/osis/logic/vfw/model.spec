#IS EXAMPLE, COPY  to category

[rootmodel:virtualfirewall] #@index
    prop:id int,,is unique id 
    prop:gid int,,grid on which firewall is running
    prop:nid int,,node on which firewall is running
    prop:name str,,
    prop:descr str,,
    prop:domain str,,free to choose domain e.g. space of customer
    prop:tcpForwardRules list(tcpForwardRule),,set of rules for tcp forwarding; when more than 1 and same source port then tcp loadbalancing
    prop:masquerade bool,True,if True then masquerading done from internal network to external
    prop:wsForwardRules list(wsForwardRule),,set of rules for reverse proxy

[model:tcpForwardRule] #@inde
    """
    """
    prop:fromPort str,,tcp port incoming
    prop:toAddr str,,ip addr where to direct to
    prop:toPort str,,tcp port where it is redirected to


[model:wsForwardRule] #@index
    prop:url str,,url domain name e.g. www.incubaid.com
    prop:toUrls str,,e.g. [192.168.1.20:3000/test/...]   #so can be port; ip; url part; when more than 1 then loadbalancing


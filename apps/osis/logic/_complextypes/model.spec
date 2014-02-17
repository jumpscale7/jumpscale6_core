#IS EXAMPLE, COPY  to category

[rootmodel:tcpForwardPolicy] #@index
    """
    """
    prop:id int,,is unique id 
    prop:tcpForwardRules list(tcpForwardRule),,set of rules for tcp forwarding; when more than 1 and same source port then tcp loadbalancing
    prop:masquerade bool,True,if True then masquerading done from internal network to external

[model:tcpForwardRule] #@inde
    """
    """
    prop:fromPort str,,tcp port incoming
    prop:toAddr str,,ip addr where to direct to
    prop:toPort str,,tcp port where it is redirected to

[rootmodel:wsForwardPolicy] #@index
    prop:id int,,is unique id 
    prop:wsForwardRules list(wsForwardRule),,set of rules for reverse proxy

[model:wsForwardRule] #@index
    prop:url str,,url domain name e.g. www.incubaid.com
    prop:toUrls str,,e.g. [192.168.1.20:3000/test/...]   #so can be port; ip; url part; when more than 1 then loadbalancing


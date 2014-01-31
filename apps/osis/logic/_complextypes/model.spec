#IS EXAMPLE, COPY  to category

[rootmodel:root] #@index
    """
    """
    prop:id int,,is unique id 
    prop:tcpPortForwardRules list(tcpPortForwardRule),,set of rules for tcp forwarding
    prop:tcpLoadBalancingRules list(tcpLoadBalancingRule),,set of rules for tcp loadbalancing
    prop:masquerade bool,True,if True then masquerading done from internal network to external


[rootmodel:securityPolicy] #@index
    """
    """
    prop:id int,,is unique id 
    prop:tcpPortForwardRules list(tcpPortForwardRule),,set of rules for tcp forwarding
    prop:tcpLoadBalancingRules list(tcpLoadBalancingRule),,set of rules for tcp loadbalancing
    prop:masquerade bool,True,if True then masquerading done from internal network to external

[model:tcpPortForwardRule] #@index
    """
    """
    prop:fromPort str,,tcp port incoming
    prop:toAddr str,,ip addr where to direct to
    prop:toPort str,,tcp port where it is redirected to

[model:tcpLoadBalancingRule] #@index
    """
    """
    prop:fromPort str,,tcp port incoming
    prop:toAddr list(str),,list of ip addr where to loadbalance to
    prop:toPort str,,tcp port where it is redirected to

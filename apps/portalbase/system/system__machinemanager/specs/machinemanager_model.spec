
[rootmodel:machine] @dbtype:osis @index
    """
    machine object
    """
    prop:id int,,
    prop:name str,,name as given by sysadmin but needs to be unique (in beginning is organization__hostname if it does not exist yet)
    prop:descr str,,
    prop:mac str,,mac of first physical network adaptor (ethernet), serves as unique id for machine
    prop:nics list(Nic),,List of id Nic objects (network interfaces) attached to this machine
    prop:disks list(Disk),,List of id Disk objects attached to this machine
    prop:realityUpdateEpoch int,,in epoch last time this object has been updated from reality
    prop:status str,,status of the vm (HALTED;INIT;RUNNING;TODELETE;SNAPSHOT;EXPORT)
    prop:hostName str,,hostname of the machine as specified by OS; is name in case no hostname is provided
    prop:cpus int,1,number of cpu assigned to the vm
    prop:hypervisorTypes list(str),,hypervisor running this machine (VMWARE;HYPERV;KVM)
    prop:acl list(ACE),,access control list
    prop:cloudspaceId int,,id of space which holds this machine
    prop:networkGatewayIPv4 str,,IP address of the gateway for this machine
    prop:organization str,,free dot notation organization name

[model:ACE]
    """
    Access control list
    """
    prop:userGroupId str,,unique identification of user or group
    prop:type str,,user or group (U or G)
    prop:right str,,right string now RWD  (depending type of object this action can be anything each type of action represented as 1 letter)

[model:Disk] @dbtype:osis
    """
    """
    prop:id int,,
    prop:name str,,name as given by sysadmin (optional)
    prop:descr str,,
    prop:realityUpdateEpoch int,,in epoch last time this object has been updated from reality
    prop:referenceId str,,name as used in hypervisor,os, ...
    prop:realityDeviceNumber int,, Number a device gets after connect
    prop:status str,,status of the vm (ACTIVE;INIT;IMAGE)
    prop:type str,,(RAW,ISCSI)
    prop:role str,,role of disk (BOOT; DATA; TEMP)
    prop:order int,,order of the disk (as will be shown in OS)
    prop:iqn str,,location of iscsi backend e.g. iqn.2009-11.com.aserver:b6d2aa75-d5ae-4e5a-a38a-12c64c787be6
    prop:diskPath str,, Holds the path of the disk
    prop:login str,,login of e.g. iqn connection
    prop:passwd str,,passwd of e.g. iqn connection
    prop:params str,,tags to define optional params

[rootmodel:Network] @dbtype:osis  @index
    """
    """
    prop:id int,,
    prop:name str,,name as given by customer
    prop:descr str,,
    prop:vlanId str,,ethernet vlan tag
    prop:subnet str,,subnet of the network
    prop:netmask str,,netmask of the network
    prop:nameservers list(str),,Nameservers
    prop:organization str,,free dot notation organization name if applicable


[model:Nic] @dbtype:osis
    """
    """
    prop:realityUpdateEpoch int,,in epoch last time this object has been updated from reality
    prop:referenceId str,,name as used in hypervisor or os
    prop:networkId int,,id of Network object
    prop:status str,,status of the nic (ACTIVE;INIT;DOWN)
    prop:deviceName str,,name of the device as on device
    prop:macAddress str,,MAC address of the vnic
    prop:ipAddresses list(str),,IP address of the vnic
    prop:params str,,pylabs tags to define optional params


# OpenWizzy Shell Commands

# basic commands

## owshell
IPython shell where OpenWizzy is already loaded 

## owlink
relink the sandbox & python libraries to all checked out openwizzy code

## owextend
installs the following repo's on the system and create the required links for python.

* openwizzy6_examples
* openwizzy6_grid
* openwizzy6_lib
* openwizzy6_portal
* dfs_io_core

## owreinstall

is sort of reinstall starting from code on trunk

* will get additional modules
* will update code
* will relink

# code management

does code mgmt for all repositories under /opt/code/openwizzy

## owcode_update
update the code repositories under /opt/code/openwizzy
will update/merge all code (always from trunk)

## owcode_push
push the code to bitbucket
will first do a owupdatecode

## owcode_commit
commit the code repositories under /opt/code/openwizzy
will no do an update first


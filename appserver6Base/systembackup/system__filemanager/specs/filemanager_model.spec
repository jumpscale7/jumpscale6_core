[rootmodel:dirobj] @nocrud
    """
    directory object metadata
    """
    prop:guid str,,is md5 of path in namespace
    prop:name str,,is the name of the directory
    prop:parents list(str),,list of guids which refer to 1 or more parent dirs
    prop:dirs list(str),,list of guids which refer to 1 or more children directories
    prop:files dict(fileobj),,list of file objects; key is the id of the fileobj
    prop:aliases list(str),,
    prop:expiration int,,epoch of expiration date
    prop:creationdate int,,epoch of creation
    prop:moddate int,,epoch of modification
    prop:history list(str),,is list of str of format: $epoch_$action_$username_$fileId $epoch_$action_$username_$dirGuid: actions are (deletedir=DD, deletefile=DF,newfile=NF,newdir=ND,modfile=MF,moddir=MD)
    prop:visible bool,True,if False will not be visible


[model:fileobj]  @nocrud
    """
    file object (metadata)
    """
    prop:id str,,is unique id which is the name of the file+ extension (case sensitive)
    prop:ext str,,extension of file
    prop:aliases list(str),,
    prop:expiration int,,epoch of expiration date
    prop:creationdate int,,epoch of creation
    prop:moddate int,,epoch of modification
    prop:visible bool,True,if False will not be visible
    prop:history list(str),,is list of str of format: $epoch_$username_$md5  


[rootmodel:contentobj]  @nocrud
    """
    the data written as content on the filesystem
    """
    prop:guid str,,will not use a typical guid but an md5
    prop:references list(str),, str is of format $dirobjguid_$fileobjid id = name of file
    prop:creationdate int,,epoch of creationdate
    prop:moddate int,,epoch of modification
    prop:visible bool,True,if False will not be visible
    prop:expiration int,,epoch of expiration date
    prop:representations dict(str),, value=$md5 key=type is PDF, JPG, PNG, TXT each image format can be appended with _$size the size is lowest size (widht or hight e.g. _1600)
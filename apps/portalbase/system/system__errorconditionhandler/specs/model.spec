[rootmodel:errorcondition] @dbtype:mem
    """
    error condition
    """
    prop:guid str,,is guid
    prop:id int,,is unique id 
    prop:appname str,,name for application which generated the error condition
    prop:actorname str,,name for actor which generated the error condition
    prop:description str,,description for private (developer) usage
    prop:descriptionpub str,,description as what can be read by endusers
    prop:level int,,1:critical, 2:warning, 3:info
    prop:category str,,dot notation e.g. machine.start.failed
    prop:tags str,,pylabs tag string, can be used to put addtional info e.g. vmachine:2323   
    prop:state str, state is "NEW","ALERT" or "CLOSED"
    prop:inittime int,,first time there was an error condition linked to this alert
    prop:lasttime int,,last time there was an error condition linked to this alert
    prop:closetime int,,alert is closed, no longer active
    prop:nrerrorconditions int,1,nr of times this error condition happened
    prop:traceback str,,optional traceback info e.g. for bug


    # [model:errorconditioncollection] 
    #     """
    #     errorcondition collection (sorted per appname__actor__hour)
    #     hour is unique id constructed as follows $yearIn4digits_$month_$dayOfMonth_$hour e.g. 2013_12_20_16 e.g. 2013_1_1_1
    #     full example for id would be system__contentmanager__2013_1_1_1

    #     str format is $guid_$id_$category_$level_$tags_$description_$descriptionpub 

    #     remark 
    #     - description are capped on 256bytes & normalized)
    #     - descroptionpub are capped on 256 bytes but not normalized
    #     - tags & category are normalized 

    #     normalization is : all lower case, doublespaces convertsTo single, ":;-_" convertsTo ","  [] to ()

    #     duplicatesearch is used to find if an new errorcondition is a duplicate or not

    #     key is 
    #     $category_$level_$tags_$description (normalized)
    #     value is the guid of the errorcondition

    #     """
    #     prop:id str,,see description of model for right structure e.g. system__contentmanager__2013_1_1_1
    #     prop:collection list(str),,list of errorconditions, for str format see description model
    #     prop:duplicatesearch dict(str),,key of dict descr see description model


    # [rootmodel:errorconditions] 
    #     """
    #     error condition dict for last e.g. hour, is used to quickly find back current errorconditions to deal with
    #     they are sorted per hour 
    #     """
    #     prop:errorconditioncollection dict(errorconditioncollection),,key of dict see descr of errorconditioncollection e.g. system__contentmanager__2013_1_1_1



def main(o,args,params,tags,tasklet):
    params.merge(args)
    
    doc=params.doc
    tags=params.tags

    params.result=""

    C="""
{{menudropdown: name:Admin
Pages:/system/Pages?space=$$space
Spaces:/system/Spaces
ReloadAll:javascript:(function loadAll() {$.ajax({'url': '/system/ReloadApplication'});(function checkSpaceIsUp(trials) {if (trials <= 0) return;setTimeout(function() {$.ajax({'url': '/system/'}).done(function(){location.reload();console.log('Reloaded');}).error(function(){checkSpaceIsUp(trials - 1)});}, 1000);})(10);})();void(0);
Logout:/system/login?user_logoff_=1
--------------
Edit:/system/edit?space=$$space&page=$$page
--------------
Access:/system/OverviewAccess?space=$$space
Reload:javascript:$.ajax({'url': '/system/ReloadSpace?name=$$space'}).done(function(){location.reload()});void(0);
ShowLogs:/system/ShowSpaceAccessLog?space=$$space
ResetLogs:/system/ResetAccessLog?space=$$space
}}
"""


    if o.apps.system.usermanager.extensions.usermanager.checkUserIsAdminFromCTX(params.requestContext):
        params.result=C        

    params.result=(params.result,doc)

    return params


def match(o,args,params,tags,tasklet):
    return True


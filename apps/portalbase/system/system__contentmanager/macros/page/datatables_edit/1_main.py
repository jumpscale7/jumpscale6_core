def main(o, args, params, tags, tasklet):

    page = args.page

    modifier = o.html.getPageModifierGridDataTables(page)

    args.expandParams()

    if "app" in args and "actor" in args and "model" in args:
        actor, model, fields, fieldids, fieldnames = o.apps.system.contentmanager.extensions.datatables.getTableDefFromActorModel(
            args.app, args.actor, args.model, excludes=["guid"])

        page = modifier.addTableFromActorModel(args.app, args.actor, args.model, fields, fieldids, fieldnames)
    else:
        raise RuntimeError("Cannot execute macro: %s, format {{datatables_edit: app:system actor:contentmanager model:space}}" % args.macrostr)

    # params.page=modifier.editTableFromURL(params.tags.tagGet("url"))

    params.result = page

    return params


def match(o, args, params, tags, tasklet):
    return True

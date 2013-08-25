
def main(o, args, params, tags, tasklet):

    params.merge(args)

    page = params.page
    tags = params.tags

    params.expandParams()

    actor = j.apps.system.usermanager
    osis = actor.models.user

    if "name" in params:
        name = params['name']
    else:
        name = ''

    pm = j.html.getPageModifierBootstrapForm(params.page)

    form = pm.getForm("a user", actor)

    form.addTextInput("name", name)
    form.addSelectFromList("city", ["ghent", "antwerp", "lochristi"], multiple=False, default="", help="")
    form.addSelectFromList("city", ["ghent", "antwerp", "lochristi"], multiple=True, default="", help="choose multiple if needed")

    pm.addForm(form)

    return params


def match(o, args, params, tags, tasklet):
    return True

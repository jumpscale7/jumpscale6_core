def main(j, args, params, tags, tasklet):
    from JumpScale.portal.docgenerator.popup import Popup
    import json
    try:
        import toml
    except Exception, e:
        out = "toml is not set up. Please update base."
        params.result = (out, args.doc)
        return params


    def _showexample():
        out = """Actions must be in yaml form.
eg:
{{actions:

[[actions]]
action = "\/restmachine\/cloudbroker\/account\/disable"
input = [ "reason",]
display = "Disable"
[actions.data]
accountname = "${name}"

[[actions]]
action = "\/restmachine\/cloudbroker\/account\/enable"
input = [ "reason",]
display = "Enable"
[actions.data]
accountname = "${name}"
}}
"""
        params.result = (out, args.doc)
        return params

    page = args.page
    macrostr = args.macrostr.strip()
    content = "\n".join(macrostr.split("\n")[1:-1])

    if not content:
        return _showexample()

    actionoptions = dict()
    actions = toml.loads(content).get('actions')
    if actions == content:
        return _showexample()

    for actiondata in actions:
        actionurl = actiondata['action']
        display = actiondata['display']
        inputs = actiondata.get('input', '')
        data = actiondata.get('data', {})
        actionid = "action-%s" % display.replace(' ', '')
        actionoptions.update({display: actionid})

        popup = Popup(id=actionid, header="Confirm Action %s" % display, submit_url=actionurl)
        if inputs:
            for var in inputs:
                popup.addText(var, var)

        for name, value in data.iteritems():
            popup.addHiddenField(name, value)

        popup.write_html(page)

    id = page.addComboBox(actionoptions, {'#': 'Choose Action'})
    page.addJS(None, """
        $(document).ready(function() {
            $("#%(id)s").change(function () {
                 var actionid = $("#%(id)s").val();
                 if (actionid != '#'){
                    $('#'+actionid).modal('show');
                 }
            });
        });
        """ % ({'id':id}))
    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True

from OpenWizzy.portal.macrolib import div_base


def main(q, args, params, *other_args):
    params.result = page = args.page
    page.addMessage('''<a href='#' onclick="$(this).parents('form')[0].reset(); return false;">Reset</a>''')
    return params

def match(q, args, params, tags, tasklet):
    return True

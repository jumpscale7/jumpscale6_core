from JumpScale.portal.macrolib import div_base


def main(o, args, params, *other_args):
    params.result = page = args.page
    page.addMessage('''<a href='#' onclick="$(this).parents('form')[0].reset(); return false;">Reset</a>''')
    return params


def match(o, args, params, tags, tasklet):
    return True

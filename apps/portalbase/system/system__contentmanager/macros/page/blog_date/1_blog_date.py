from OpenWizzy.portal.macrolib.blog import BlogPost


def main(o, args, params, *other_args):
    params.result = page = args.page
    post = BlogPost(args.doc.path)
    page.addMessage(post.date)
    return params


def match(o, args, params, tags, tasklet):
    return True

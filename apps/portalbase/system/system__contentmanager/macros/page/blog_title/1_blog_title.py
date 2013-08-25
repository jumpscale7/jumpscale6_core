from JumpScale.portal.macrolib.blog import BlogPost


def main(o, args, params, *other_args):
    params.result = page = args.page
    post = BlogPost(args.doc.path)
    page.addMessage(post.title)
    return params


def match(o, args, params, tags, tasklet):
    return True

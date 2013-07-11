from pylabs.blog import BlogPost


def main(q, args, params, *other_args):
    params.result = page = args.page
    post = BlogPost(args.doc.path)
    page.addMessage(post.title)
    return params


def match(q, args, params, tags, tasklet):
    return True

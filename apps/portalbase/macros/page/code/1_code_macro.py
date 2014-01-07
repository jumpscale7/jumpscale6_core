
def main(j, args, params, tags, tasklet):
    page = args.page
    page.addBootstrap()
    macrostr = args.macrostr.strip()
    content = "\n".join(macrostr.split("\n")[1:-1])
    content = content.replace("\{", "{")
    content = content.replace("\}", "}")

    #template="python"
    #linecolor="#eee"

    page.addCodeBlock(content, edit=False, exitpage=True, spacename='', pagename='',linenr=False,\
        linecolor="#eee",linecolortopbottom="1px solid black")

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

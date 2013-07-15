
def main(o,args,params,tags,tasklet):
    page = args.page
    page.addBootstrap()
    macrostr=args.macrostr.strip()
    content="\n".join(macrostr.split("\n")[1:-1])
    content=content.replace("\{","{")
    content=content.replace("\}","}")

    page.addCodeBlock(content,edit=False)

    params.result = page
    return params


def match(o,args,params,tags,tasklet):
    return True



def main(o, args, params, tags, tasklet):

    page = args.page
    page.addBootstrap()
    navStr = args.cmdstr

    page.addMessage("<div class='well sidebar-nav'>")
    page._hasSidebar = True

    if args.doc.navigation != "":
        if navStr.strip() == "":
            navStr = args.doc.navigation + "\n"
        if navStr.strip() != "" and navStr[-1] != "\n":
            navStr += "\n"
            navStr += args.doc.navigation
        if navStr[-1] != "\n":
            navStr += "\n"

    def clean(txt):
        lines = txt.split("\n")
        lines = [item.strip() for item in lines if item.strip() != ""]
        if lines[0] == "<p></p>":
            lines.pop(0)
        if lines[0] == "<ul>":
            lines.pop(0)
        if lines[-1] == "</ul>":
            lines.pop()
        return "\n".join(lines)

    items = ""
    # out=""
    for line in navStr.split("\n"):
        line = line.strip()

        if line != "":
            if line.find("include:") == 0:
                name = line.replace("include:", "").strip()
                doc = args.doc.preprocessor.docGet(name)
                line, doc2 = doc.executeMacrosDynamicWiki()
                html = clean(doc.getHtmlBody())
                page.addMessage(html)
            if line.find("{{") == 0:
                try:
                    line, doc2 = args.doc.preprocessor.macroexecutorWiki.execMacrosOnContent(content=line, doc=args.doc)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    raise RuntimeError(
                        "**ERROR: error executing macros for line:%s and for doc:%s, this happens inside navigation macro." % (line, args.doc.name))

                convertor = j.tools.docgenerator.getConfluence2htmlConvertor()
                convertor.convert(line, args.page, args.doc)
            # out+=line+"\n"
            else:
                if len(line.split(":")) > 2:
                    name, target, icon = line.split(":", 2)
                elif len(line.split(":")) > 1:
                    name, target = line.split(":", 1)
                    icon = ""
                else:
                    name = line
                    target = ""
                    icon = ""
                line2 = "<li><a href=\"%s\"><i class=\"%s\"></i>%s</a></li>" % (target.strip(), icon.strip(), name.strip())
                items += "%s\n" % line2

    page.addMessage(items)
    page.addMessage("</div>")

    params.result = page

    return params


def match(o, args, params, tags, tasklet):
    return True

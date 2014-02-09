import random
def main(j, args, params, tags, tasklet):
    page = args.page
    page.addJS(jsLink='/lib/plantuml/rawdeflate.js')
    page.addJS(jsLink='/lib/plantuml/plantuml.js')

    random_id = random.randint(1, 9999999)
    page.addMessage('<textarea id="uml_{}" style="display: none">{}</textarea>'.format(random_id, args.cmdstr))
    page.addMessage('<img id="uml_im_{}">'.format(random_id))
    page.addJS(header=False, jsContent='''
               compress(document.getElementById('uml_{0}').value, "uml_im_{0}")
               '''.format(random_id))


    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True

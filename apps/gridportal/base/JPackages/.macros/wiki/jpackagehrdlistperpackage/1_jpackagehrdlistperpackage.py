
def main(j, args, params, tags, tasklet):

    j.packages.docGenerator.getDocs()

    hrdlist1,hrdlist2=j.packages.docGenerator.getHrdLists()

    params.result = (hrdlist1, args.doc)

    return params


def match(j, args, params, tags, tasklet):
    return True

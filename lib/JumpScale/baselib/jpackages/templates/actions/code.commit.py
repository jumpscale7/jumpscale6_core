
#if customizations are required when doing a commit of the jpackage

def main(jp):
    recipe=jp.getCodeMgmtRecipe()
    recipe.commit()


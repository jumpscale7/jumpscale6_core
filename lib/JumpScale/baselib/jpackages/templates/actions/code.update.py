
#if customizations are required when doing the update of the code of the jpackage

def main(jp,force=False):
    recipe=jp.getCodeMgmtRecipe()
    recipe.update(force=force)


import os

def main(q,args,params,tags,tasklet):
    
    page = args.page
    params.result = page

    page.addJS("/lib/bootstrap-image-gallery/js/load-image.min.js")
    page.addJS("/lib/bootstrap-image-gallery/js/bootstrap-image-gallery.min.js")
    page.addCSS("/lib/bootstrap-image-gallery/css/bootstrap-image-gallery.min.css")
    C = """<div class="container-fluid"> 
    <div id="gallery" data-toggle="modal-gallery" data-target="#modal-gallery">"""
    pars = args.expandParamsAsDict()
    
    """
    This is code for using buckets can be extented later.
    buckets = q.core.appserver6.runningAppserver.webserver.bucketsloader.buckets
    if pars.has_key('picturebucket') and pars['picturebucket'] in buckets:
        bucket = buckets[pars['picturebucket']]
        files = q.system.fs.listFilesInDir(bucket.model.path)
    else:
        files = []
    """
    space = q.core.appserver6.runningAppserver.webserver.spacesloader.spaces[args.doc.getSpaceName()]
    imagedir = q.system.fs.joinPaths(space.model.path,'.files','img')
    if not pars.has_key('title'):
        title =""
    else:
        title = pars['title']
    if pars.has_key('picturedir'):
        baseurlpath = "$$space/.files/img/%s" %  pars['picturedir']
        fullimagepath = q.system.fs.joinPaths(imagedir, pars['picturedir'])
    else:
        baseurlpath = "images/$$space/"
        localpath = args.doc.path
        fullimagepath = q.system.fs.getDirName(localpath)
    
    allfiles = q.system.fs.listFilesInDir(fullimagepath, filter="*.jpg", case_sensitivity='insensitive')
    allfiles+=(q.system.fs.listFilesInDir(fullimagepath, filter="*.png", case_sensitivity='insensitive'))
    allfiles+=(q.system.fs.listFilesInDir(fullimagepath, filter="*.bmp", case_sensitivity='insensitive'))
    allfiles+=(q.system.fs.listFilesInDir(fullimagepath, filter="*.jpeg", case_sensitivity='insensitive'))
    allfiles+=(q.system.fs.listFilesInDir(fullimagepath, filter="*.gif", case_sensitivity='insensitive'))

    
    smallfiles = q.system.fs.listFilesInDir(fullimagepath, filter="s_*.*")
    bigfiles = [x for x in allfiles if x not in smallfiles]

    thumb_size = pars.get('thumb_size', args.doc.docparams.get('thumb_size', '150x100'))

    thumb_size = [int(x) for x in thumb_size.split('x')]

    for i in bigfiles:
        basefile = q.system.fs.getBaseName(i)
        bigpath = "/%s/%s" % (baseurlpath, basefile)
        
        smallpath = "/%s/s_%sx%s_%s" % (baseurlpath, thumb_size[0], thumb_size[1], basefile)

        #link = '<a data-gallery = "gallery" data-href=%s title=%s><img src=%s></a>' % (bigpath, title, smallpath)
        
        # Generate a thumbnail from the existing image
        thumbnail_path = os.path.join(fullimagepath, 's_{0}x{1}_{2}'.format(thumb_size[0], thumb_size[1], basefile))
        if not os.path.exists(os.path.dirname(thumbnail_path)):
            os.makedirs(os.path.dirname(thumbnail_path))
        if not q.system.fs.exists(thumbnail_path):
            q.tools.imagelib.resize(i, thumbnail_path, width=thumb_size[0], overwrite=False)
        link = '<a data-gallery = "gallery" data-href=%s title=%s><img src="%s" /></a>' % (bigpath, title, smallpath, )
        C += link
    
    C += '</div></div>'

    
      

    C += """
    <div id="modal-gallery" class="modal modal-gallery hide fade modal-loading " tabindex="-1"  aria-hidden="true">
    <div class="modal-header">
        <a class="close" data-dismiss="modal">&times;</a>
        <h3 class="modal-title"></h3>
    </div>
    <div class="modal-body"><div class="modal-image"></div></div>
    <div class="modal-footer">
        <a class="btn btn-primary modal-next">Next <i class="icon-arrow-right icon-white"></i></a>
        <a class="btn btn-info modal-prev"><i class="icon-arrow-left icon-white"></i> Previous</a>
        <a class="btn btn-success modal-play modal-slideshow" data-slideshow="5000"><i class="icon-play icon-white"></i> Slideshow</a>
    </div>
    </div>
    """
    page.addMessage(C)
    return params


def match(q,args,params,tags,tasklet):
    return True


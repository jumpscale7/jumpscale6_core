from itertools import count
import os

def main(j, args, params, *other_args):
    params.result = page = args.page
    page.addCSS(cssContent=''' 
        .description h2.small{
            font-size: 170%;
        }
        .description h2.medium{
            font-size: 200%;
        }
        .description h2.large{
            font-size: 250%;
        }
        .slides .description p{
            line-height: 1.4em;
        }
        .slides .description p.small{
            font-size: 18px;
        }
        .slides .description p.medium{
            font-size: 21px;
        }
        .slides .description p.large{
            font-size: 25px;
        }
        /* this solved a conflict with bootstrap */
        .current.hide{ 
            display: inherit; 
        }
     ''')
    page.addCSS('/jslib/titledcontentslideshow/css/normalize.css')
    page.addCSS('/jslib/titledcontentslideshow/css/component.css')
    page.addJS('/jslib/titledcontentslideshow/js/modernizr.custom.js')
    page.addJS('/jslib/titledcontentslideshow/js/tiltSlider.js')
    hrd = j.core.hrd.getHRD(content=args.cmdstr)

    space = j.core.portal.active.spacesloader.spaces[args.doc.getSpaceName()]
    imagedir = j.system.fs.joinPaths(space.model.path, '.files', 'img/')
        
    slides = []
    for i in count(1):
        slide = {}

        slide['Title'] = hrd.get('slide.{}.title.text'.format(i), default='').replace(r'\n', '<br />')
        if not slide['Title']:
            break
        slide['TitleSize'] = hrd.get('slide.{}.title.text.size'.format(i), default='medium')
        slide['BackgroundColor'] = hrd.get('slide.{}.background.color'.format(i), default='')
        if os.path.isfile(imagedir + hrd.get('slide.{}.image.path'.format(i), default='')):
            # check if can find image under .files/img by the given name
            slide['ImagePath'] = '/$$space/.files/img/' + hrd.get('slide.{}.image.path'.format(i), default='')
        else:
            # image from full url
            slide['ImagePath'] = hrd.get('slide.{}.image.path'.format(i), default='')
        
        slide['BodyText'] = hrd.get('slide.{}.body.text'.format(i), default='').replace(r'\n', '<br />')
        slide['BodyTextSize'] = hrd.get('slide.{}.body.text.size'.format(i), default='small')
        slide['ButtonText'] = hrd.get('slide.{}.button.text'.format(i), default='')
        slide['ButtonLink'] = hrd.get('slide.{}.button.link'.format(i), default='')
        slide['ButtonStyle'] = hrd.get('slide.{}.button.style'.format(i), default='').lower()
        slides.append(slide)


    page.addMessage('''
         <div class="container">
            <div class="slideshow" id="slideshow">
                <ol class="slides">
        ''')

    for slide in slides:
        if slides.index(slide) == 0:
            page.addMessage('''<li class="current" style="background-color: #{BackgroundColor}">'''.format(**slide))
        else:
            page.addMessage('''<li style="background-color: #{BackgroundColor}">'''.format(**slide))

        page.addMessage('''
                <div class="description">
                    <h2 class="{TitleSize}">{Title}</h2>
                    <p class="{BodyTextSize}">{BodyText}</p>
        '''.format( **slide))
        
        if(slide['ButtonText']):
            page.addMessage('''
                <a href="{ButtonLink}" class="btn btn-{ButtonStyle}">{ButtonText}</a>
            '''.format(**slide))

        page.addMessage('''
                </div>
                <div class="tiltview col">
                    <a href="#"><img src="{ImagePath}"/></a>
                </div>
            </li>
        '''.format( **slide))

    page.addMessage('''
                </ol>
            </div>
        </div>
        ''')

    page.addJS(jsContent='''
        $(function() {
            new TiltSlider( document.getElementById( 'slideshow' ) );
        });
        ''')
    return params


def match(*whatever):
    return True

import os

def main(j, args, params, tags, tasklet):
	page = args.page
	page.addCSS(cssContent=''' 
		.bigpicture{
			margin: 10px 0 15px 0;
		}
		.bigpicture-container{
			text-align: center;
		}
		.subtitle{
			margin-bottom: 10px;
			display: block;
		}
		.subtitle-paragraph{
			margin-bottom: 5px;
		}
		.bigpicture-container h1.small{
			font-size: 25px;
		}
		.bigpicture-container h1.medium{
			font-size: 30px;
		}
		.bigpicture-container h1.large{
			font-size: 35px;
		}
		.bigpicture-container h1.xlarge{
			font-size: 40px;
		}
		.subtitle.small, .subtitle-paragraph.small, .subtitle-link.small{
			font-size: 14px;
		}
		.subtitle.medium, .subtitle-paragraph.medium, .subtitle-link.medium{
			font-size: 16px;
		}
		.subtitle.large, .subtitle-paragraph.large, .subtitle-link.large{
			font-size: 18px;
		}
	 ''')
	hrd = j.core.hrd.getHRD(content=args.cmdstr)
	bigpicture = {}
	bigpicture['picturePath'] = ""
	bigpicture['titleText'] = getattr(hrd, 'title_text', '')
	bigpicture['titleSize'] = getattr(hrd, 'title_size', 'medium')
	bigpicture['subtitleText'] = getattr(hrd, 'subtitle_text', '')
	bigpicture['subtitleSize'] = getattr(hrd, 'subtitle_size', 'medium')
	bigpicture['paragraphText'] = getattr(hrd, 'paragraph_text', '')
	bigpicture['paragraphSize'] = getattr(hrd, 'paragraph_size', 'medium')
	bigpicture['subtitleLink'] = getattr(hrd, 'subtitle_link', '')
	bigpicture['subtitleLinkText'] = getattr(hrd, 'subtitle_link_text', '')
	bigpicture['subtitleLinkSize'] = getattr(hrd, 'subtitle_link_size', 'medium')

	# check if can find image under .files/img by the given name
	space = j.core.portal.active.spacesloader.spaces[args.doc.getSpaceName()]
	imagedir = j.system.fs.joinPaths(space.model.path, '.files', 'img/')
	if os.path.isfile(imagedir + getattr(hrd, 'picture_path', '')):
		bigpicture['picturePath'] = '/$$space/.files/img/' + getattr(hrd, 'picture_path', '')
	else:
		# image from full url
		bigpicture['picturePath'] = getattr(hrd, 'picture_path', '')

	page.addMessage('''
		<div class="bigpicture-container">
			<div class="container">
				<h1 class="title {titleSize}">{titleText}</h1>
				<div class="span10 offset1">
					<img class="bigpicture img-rounded" src="{picturePath}">
					<div class="subtitle-container">
						<strong class="subtitle {subtitleSize}">{subtitleText}</strong>
						<p class="subtitle-paragraph {paragraphSize}">{paragraphText}</p>
						<a class="subtitle-link {subtitleLinkSize}" href="{subtitleLink}">{subtitleLinkText}</a>
					</div>
				</div>
			</div>
		</div>
	 '''.format(**bigpicture))

	params.result = page
	return params


def match(j, args, params, tags, tasklet):
    return True

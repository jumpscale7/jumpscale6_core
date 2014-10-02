from itertools import count

def main(j, args, params, tags, tasklet):
	page = args.page
	page.addBootstrap()
	page.addCSS(cssContent=''' 
		.comparison-block{
			border: 1px solid #C9D4FA;
			margin-bottom: 10px;
		}
		.comparison-block:hover{
			border: 1px solid #B0D7D5;
		}
		.comparison-block:hover .title{
			background-color: #62a29e;
			color: #fff;
		}
		.comparison-block:hover .title *{
			color: #fff;
		}
		.comparison-footer{
			padding: 10px 0;
			border-top: 1px solid #C9D4FA;
			margin-top: 10px;
		}
		.comparison-footer button{
			margin-top: 8px;
		}
		.tex-center{
			text-align: center;
		}
		.title{
			background: #C7E1E0;
			padding: 15px;
		}
		.title small, .price small, .comparison-footer small{
			color: #8D8A8A;
		}
		.title p{
			margin-bottom: 5px;
			color: #4F918D;
			font-weight: bold;
			font-size: 18px;
		}
		.price{
			padding-top: 15px;
			background-color: #E5E5E5;
			border-top: 1px solid #C9D4FA;
			border-bottom: 1px solid #C9D4FA;
			margin-bottom: 10px;
			padding-bottom: 10px;
		}
		.price p{
			font-size: 30px;
			color: #767677;
			margin-bottom: 0;
		}
		.property{
			padding: 3px;
			font-size: 90%;
			padding-left: 8px;
			cursor: default;
		}
		.property:hover{
			background-color: #62a29e;
			color: #fff;
		}
		.currency{
			font-size: 60%;
		}
	 ''')
	hrd = j.core.hrd.getHRD(content=args.cmdstr)

	currency = getattr(hrd, 'currency', '')

	blocks = []
	for i in count(1):
		try:
		    block = {}
		    block['Title'] = getattr(hrd, 'block_{}_title_text'.format(i), '')
		    block['TitleSize'] = getattr(hrd, 'block_{}_title_size'.format(i), '')
		    block['SubtitleText'] = getattr(hrd, 'block_{}_subtitle_text'.format(i), '')
		    block['SubtitleSize'] = getattr(hrd, 'block_{}_subtitle_size'.format(i), '')
		    block['Price'] = getattr(hrd, 'block_{}_price'.format(i))
		    block['PriceSubtitle'] = getattr(hrd, 'block_{}_price_subtitle'.format(i), '')
		    block['Property1'] = getattr(hrd, 'block_{}_property_1'.format(i), '')
		    block['Property2'] = getattr(hrd, 'block_{}_property_2'.format(i), '')
		    block['Property3'] = getattr(hrd, 'block_{}_property_3'.format(i), '')
		    block['Property4'] = getattr(hrd, 'block_{}_property_4'.format(i), '')
		    block['OrderButtonText'] = getattr(hrd, 'block_{}_order_button_text'.format(i), '')
		    block['OrderButtonStyle'] = getattr(hrd, 'block_{}_order_button_style'.format(i), '').lower()
		    block['OrderButtonSubtext'] = getattr(hrd, 'block_{}_order_button_subtext'.format(i), '')
		    block['OrderButtonSubLink'] = getattr(hrd, 'block_{}_order_button_link'.format(i), '')
		    blocks.append(block)
		except AttributeError:
		    break

	page.addMessage('''
		<div class="container">
			<div class="row">
		''')

	for block in blocks:
		block['i'] = 12 / len(blocks)
		page.addMessage('''
				<div class="span{i} comparison-block">
					<div class="title tex-center {TitleSize}">
						<p>{Title}</p>
						<small>{SubtitleText}</small>
					</div>
					<div class="price tex-center">
						<p><small class="currency">{currency}</small>{Price}</p>
						<small>{PriceSubtitle}</small>
					</div>
		'''.format(currency=currency, **block))

		if(block['Property1']):
			page.addMessage('''
				<div class="property property1">
					{Property1}
				</div>
			'''.format(currency=currency, **block))

		if(block['Property2']):
			page.addMessage('''
				<div class="property">
					{Property2}
				</div>
			'''.format(currency=currency, **block))

		if(block['Property3']):
			page.addMessage('''
				<div class="property">
					{Property3}
				</div>
			'''.format(currency=currency, **block))

		if(block['Property4']):
			page.addMessage('''
				<div class="property">
					{Property4}
				</div>
			'''.format(currency=currency, **block))

		page.addMessage('''
					<div class="comparison-footer tex-center">
						<small>{OrderButtonSubtext}</small>
						<br/>
						<button href="{OrderButtonSubLink}" class="btn btn-{OrderButtonStyle}" type="button">{OrderButtonText}</button>
					</div>
				</div>
		'''.format(**block))

	page.addMessage('''</div></div>''');
	params.result = page
	return params


def match(j, args, params, tags, tasklet):
    return True

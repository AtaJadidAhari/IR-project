# -*- coding: utf-8 -*-
import scrapy


class ArticleSpider(scrapy.Spider):
	starting_urls = []
	print('How many links do you want as starting links? (Enter -1 if you want to use the dafault urls given in the project doc)')
	num_of_links = int(input())
	if num_of_links == -1:
		 starting_urls = [
		'https://www.semanticscholar.org/paper/The-Lottery-Ticket-Hypothesis%3A-Training-Pruned-Frankle-Carbin/f90720ed12e045ac84beb94c27271d6fb8ad48cf',
		'https://www.semanticscholar.org/paper/Attention-is-All-you-Need-Vaswani-Shazeer/204e3073870fae3d05bcbc2f6a8e263d9b72e776',
		'https://www.semanticscholar.org/paper/BERT%3A-Pre-training-of-Deep-Bidirectional-for-Devlin-Chang/df2b0e26d0599ce3e70df8a9da02e51594e0e992'
		]
	else:

		for i in range(num_of_links):
			starting_urls.append(input("Please enter starting urls, one by one\n"))
	print('How many papers do you want to be crawled? (Enter -1 if you want to use the dafault number, i.e. 2000)')
	
	num_of_crawled = int(input())
	if num_of_crawled == -1:
		num_of_crawled = 2000
	visited = []
	
	name = "article_spider"
	start_urls = starting_urls
	custom_settings={ 'FEED_URI': "crawled.json",
					'FEED_FORMAT': 'json'}

	def parse(self, response):
		if (len(ArticleSpider.visited)) >= ArticleSpider.num_of_crawled:
			return
		id = response.url.split("/")[-1]
		ArticleSpider.visited.append(id)
		title = response.css(".fresh-paper-detail-page__header > h1 ::text").extract_first()
		try:
			
			pub_date = int(response.css(".paper-meta-item + li > span > span > span > span ::text").extract_first())
		except:
			try:
				
				pub_date = int(response.css(".paper-meta-item + li > span > span + span > span > span ::text").extract_first())
			except:
				pub_date = ''
		authors = response.css(".paper-meta-item > span > span > span > a > span > span ::text").extract()
		more_authors = response.css(".more-authors-label").extract()
		
		abstract = ''
		try:
			abstract = response.css(".abstract__text ::text").extract_first()
		except:
			pass 
		if abstract == None:
			abstract = ''
			
		
		references = response.css(".references > div + div > div > div + div > div > div > h2 > a::attr(href)").extract()
		
		
		
		
		
		
		
		
		
		
		yield {
			'id': id,
			'title': title,
			'authors' : authors,
			'date': pub_date,
			'abstract' : abstract,
			'references': [i.split('/')[-1] for i in references[:10]],
		}
		
		
		for next in  references[:10]:
			yield scrapy.Request(
				response.urljoin(next),
				callback=self.parse
			)
		

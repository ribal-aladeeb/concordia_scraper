import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import logging
import os
import utils
import sys
from utils import CACHE_DIR


class ConcoSpider(scrapy.spiders.CrawlSpider):
    documents_folder = os.path.join(CACHE_DIR,'documents')
    name = 'ConcordiaSpider'
    results_filename = 'url_scraped.txt'
    allowed_domains = ['www.concordia.ca']
    start_urls = ['https://www.concordia.ca']
    rules = (
        Rule(
            LinkExtractor(
                deny=(
                    r'^(https://www.concordia.ca/fr)',  # the french website will ruin the index so ignore it
                    r'^(?!https://www.concordia.ca).+', # don't go to subdomains within concordia.ca because it could derail scraping
                    r'(sort=[a-z][A-Z]+)$',              # some pages allow sorting and we don't need each sort permutation (because we use bag of words model)
                    # for some absurd reason concordia allows many empty pages for a given person search so ignore anything after 10 pages
                    # https://www.concordia.ca/news/authors/j-cohen.html?page=940
                    # https://www.concordia.ca/news/authors/j-cohen.html?page=937
                    # https://www.concordia.ca/news/authors/j-cohen.html?page=938
                    # https://www.concordia.ca/news/authors/j-cohen.html?page=856
                    r'(page=[1-9][0-9]+)$',
                ),
            ),
            follow=True,
            callback='parse'
        ),
    )

    max_visited_pages = 5
    num_visited = 0
    unique_urls = set()
    # visited_pages = set()

    def parse(self, response):

        if self.max_visited_pages <= self.num_visited:
            raise scrapy.exceptions.CloseSpider()

        logging.info(f'Scraping doc {self.num_visited+1}\t{response.url}')
        if response.url in self.unique_urls:
            logging.info(f'URL already visited... skipping it')
            yield

        self.num_visited += 1
        self.unique_urls.add(response.url)

        docID = self.num_visited
        scraped_doc_folder = os.path.join(self.documents_folder, str(docID))
        url_filename = os.path.join(scraped_doc_folder, 'url')
        text_filename = os.path.join(scraped_doc_folder, 'text')
        utils.ensure_dir_exists(scraped_doc_folder)

        with open(self.results_filename, mode='a') as f:
            f.write(f'{response.url}\n')

        with open(url_filename, mode='w') as f:
            f.write(response.url)

        rawtext = BeautifulSoup(response.body, 'lxml').get_text()
        with open(text_filename, mode='w') as f:
            f.write(rawtext)


def main():
    number_of_pages_to_scrape = 10
    if 1 < len(sys.argv):
        try:
            number_of_pages_to_scrape = int(sys.argv[1])
        except ValueError as e:
            print(e)
            print('Please try again but make sure you pass an integer argument.')
        except Exception as e:
            raise e

    process = CrawlerProcess(settings={
        'CONCURRENT_REQUESTS': 1,
        'ROBOTSTXT_OBEY': True,
        'LOG_LEVEL': 'INFO'
    })

    ConcoSpider.max_visited_pages = number_of_pages_to_scrape
    if os.path.isfile(ConcoSpider.results_filename):
        os.remove(ConcoSpider.results_filename)
    # utils.ensure_dir_exists(ConcoSpider.documents_folder)
    process.crawl(ConcoSpider)
    process.start()
    print(f"\nDone Scraping: You can find all URLs collected in {ConcoSpider.results_filename}.")
    print(f"You can find each document ID's URL and extracted text in {ConcoSpider.documents_folder}/ID")


if __name__=="__main__":
    main()

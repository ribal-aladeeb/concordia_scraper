# concordia_scraper

Scrape https://www.concordia.ca and create a queriable inverted index

# Environment and Dependencies

I you have conda installed on you machine, simply type the following commands.
Otherwise open the environment.yml and manual install the dependencies listed
using pip.

```
conda env create -f environment.yml
conda activate crawler
```


# TL;DR
1. Crawl and Scrape N pages from the concordia website
```
python crawl.py N   #replace N with the number of documents you wish to scrape
```
2. Index the documents:
```
python indexer.py
```
3. Query the index:
```
python query.py
```

# Break down of this project

## There are three main modules in this project.

1. Crawler/Scraper
2. Indexer
3. Querier

## 1. Crawler/Scraper
This module will crawl www.concordia.ca and find all the subpages associated
with the domain name. It will sequentially scrape the pages, extracting the text
contents from the body of the html. It will then store that information in
cache/documents. For each docID, this module will create
cache/documents/docID/text and cache/documents/docID/url text files. The former
contains the extracted text and the latter contains the url of the webpage
scraped to representing this document. By default the crawler will scrape 10
pages (which is no where nearly enough to create an index) to show the effect of
running the module. You can then specify (as shown in the TLDR) a specific
number of pages that you wish to scrape. Please note that everytime the crawler
runs it deletes the cache/document  (i.e. all documents) if it already exists.
So If you do download a large chunk of documents please be careful of
accidentally deleting them by running the crawler multiple times. In my case, I
ran ```$ python crawl.py 100000``` but I interrupted the scraping after ~22
thousand documents. Note that rate of webpages scraped per minute will decrease
overtime. I had about 250-350 documents/minute at the very beginning but after
20,000 documents I was only scraping only about 4-10 documents/minute. I am not
quite sure why this happens. My first intuition is that as more documents are
crawled and the list of visited webpages grows, the crawler will encounter the
same webpages over and over because it follows links recursively. You will not
scrape the same document twice tho because the crawler will ensure that the
current document has not already been scraped before downloading it.

## 2. Creating the Inverted Index

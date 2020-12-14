# concordia_scraper

Scrape https://www.concordia.ca and create a queriable inverted index. Please
note that the conventions for robot exclusion have been respected. You can see
[line 87](https://github.com/ribal-aladeeb/concordia_scraper/blob/5b4ee54d904670aa1a8c9e5f1e9b18450607507f/crawl.py#L87)
of the crawler module.

# Environment and Dependencies

I you have conda installed on you machine, simply type the following commands.
Otherwise open the environment.yml and manual install the dependencies listed
using pip.

```

conda env create -f environment.yml
conda activate crawler
```

# TL; DR

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
`cache/documents/` . For each docID, this module will create
`cache/documents/docID/text` and `cache/documents/docID/url` text files.
The former contains the extracted text and the latter contains the url of the
webpage scraped to representing this document. By default the crawler will
scrape 10 pages (which is no where nearly enough to create an index) to show the
effect of running the module. You can then specify (as shown in the TLDR) a
specific number of pages that you wish to scrape. Please note that everytime the
crawler runs it deletes the cache/document  (i.e. all documents) if it already
exists. So If you do download a large chunk of documents please be careful of
accidentally deleting them by running the crawler multiple times. In my case, I
ran `$ python crawl.py 100000` but I interrupted the scraping after ~22
thousand documents. Note that rate of webpages scraped per minute will decrease
over time. I had about 250-350 documents/minute at the very beginning but after
20, 000 documents I was only scraping ~ 4-10 documents/minute. I am not
quite sure why this happens. My first intuition is that as more documents are
crawled and the list of visited webpages grows, the crawler will encounter the
same webpages over and over because it follows links recursively. You will not
scrape the same document twice tho because the crawler will ensure that the
current document has not already been scraped before downloading it.

## 2. Creating the Inverted Index

This module will create an inverted index of the following format:
{term: [df, (docID, tf), (docID, tf), ... , (docID, tf)]}.

`term` is a unique term found in the documents

`df` stands for document frequencie: the number of document in which this term
appears at least once.

`(docID, tf)` This is a pair of document ID and term frequency (the number of times
that this term appears in said docID).



<br>When you run the indexer it will prompt you as follows:
```
Do you wish to stem your index? [Y]es/[N]o:
```
It is strongly suggested that you stem your index. Stemming removes the suffix
of words and only keeps their root. Stemming helps in acheiving a better recall
which helps in retreiving a larger portion of the documents that are relevant to
your queries. The first thing to note is that stemming will roughly increase the
runtime of indexing by a factor of 8. This is not very problematic if you
haven't scraped lots of documents. However, if you do scrape tens of thousands of
documents this will be the difference between seconds and minutes of indexing.
The second thing to note is that you need to remember whether your index was
stemmed when querying later on.






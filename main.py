#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup as BS
from collections import OrderedDict, Counter
import json
import csv

def fetch_url(url):
    return urllib2.urlopen(url).read()

def curate_urls(base_url):
    domain = urlparse(base_url).netloc
    soup = BS(fetch_url(base_url), 'html.parser')
    anchors = soup.find_all('a')
    return [tag.attrs['href'] for tag in anchors if domain in tag.attrs['href']]

def categories(soup):
    tag = soup.find('nav', 'categories')
    return {subtag["data-id"]: subtag.string for subtag in tag.find_all('a', attrs={'data-id': True})}

def startup_node(soup):
    return soup.find_all('div', attrs={'data-id':True})

def all_startup_categories(tags, all_categories):
    ids = []
    for tag in tags:
        ids.extend(list(set(tag['class']) & set(all_categories)))
    return ids

def freq_count(arr, mapping):
    count = Counter(arr)
    return {mapping[k]: count[k] for k in count}

def main():
    urls = curate_urls('http://startups-list.com/')
    with open('trend.csv', 'wb') as f:
        writer = csv.writer(f)
        header = ['city', 'category', 'count']
        writer.writerow(header)
        for url in urls:
            subdomain = urlparse(url).netloc.split('.')[0]
            html = fetch_url(url)
            soup = BS(html, 'html.parser')
            category_mapping = categories(soup)
            category_ids = category_mapping.keys()
            companies = startup_node(soup)
            arr = all_startup_categories(companies, category_ids)
            category_count = freq_count(arr, category_mapping)
            ordered_count = OrderedDict(sorted(category_count.items(), key=lambda item: item[1]))
            for k in ordered_count:
                writer.writerow([subdomain, k.encode('utf-8'), ordered_count[k]])
            print url, '# of startups: ', len(companies)
            print json.dumps(ordered_count, indent=4)

if __name__ == '__main__':
    main()

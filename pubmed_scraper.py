#!/usr/bin/env python
# coding: utf-8

# In[11]:


# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 17:10:18 2022
@author: AZhuparris
"""

#%%
# Purpose of this script:
# Allows users to define keywords (along with a given timeframe) for their Pubmed search. The script returns a pandas dataframe and csv file with the following information: 'authors', 'ArticleTitle', 'journal_title', 'volume', 'date', 'pubmed', 'doi_pii_str', 'abstract','population'*, 'symptoms'*, 'bacteria'.* Users can also add a custom column(s) as well.
# Note that * columns return a limited number of search terms.


#import libraries


# Purpose of this script:
# Allows users to define keywords (along with a given timeframe) for their Pubmed search. The script returns a pandas dataframe and csv file with the following information: 'authors', 'ArticleTitle', 'journal_title', 'volume', 'date', 'pubmed', 'doi_pii_str', 'abstract','population'*, 'symptoms'*, 'bacteria'.* Users can also add a custom column(s) as well.
# Note that * columns return a limited number of search terms.


#import libraries
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
import requests

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

import urllib.request
import urllib.parse
import urllib.error

import ssl
import json
import calendar

# inspiration for code from https://github.com/PhilippeCodes/Web-Scraping-PubMed/blob/master/Scrape_PubMed.py


def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist


def subpop(x):
    ans = [y for y in list_of_pop if y.lower() in x]
    return ', '.join(unique_list(ans))


def subcustom(x):
    ans = [y for y in customKeywordList if y.lower() in x]
    return ', '.join(unique_list(ans))


def return_unique_string(a):
    a = ' '.join(unique_list(a.split()))
    return a


def strip_brackets(s):
    '''
    Objective: Delete brackets from titles
    '''
    no_brackets = ""
    remove_char = ['[', ']']
    for char in s:
        if char not in remove_char:
            no_brackets += char
    return no_brackets


def get_bibliography(soup):
    '''
    Objective: Extracts all bibliography information
    '''
    article = soup.find('article')
    journal = soup.find('journal')

    try:
        authorlist = article.find('authorlist')

        authors = ""
        if authorlist:
            for i in range(len(authorlist.find_all('lastname'))):
                initial = authorlist.find_all('initials')[i].text
                authors += initial
                authors += '. '
                last_name = authorlist.find_all('lastname')[i].text
                authors += last_name
                if i == len(authorlist.find_all('lastname'))-2:
                    authors += ' and '
                elif i != len(authorlist.find_all('lastname'))-1:
                    authors += ', '
            authors += ", "
    except:
        authors = 'not found'
    
    try:
        article_title = ''
        if article.find('articletitle'):
            article_title = '"'
            title_str = article.find('articletitle').text
            title_str = strip_brackets(title_str)
            article_title += title_str
            if article_title[-1] == '.':
                article_title += '", '
            else:
                article_title += '," '
    except:
        article_title = 'not found'
    
    try:
        volume = ''
        if journal.find('volume'):
            volume = journal.find('volume').text
            if soup.find('issue'):
                volume += '('
                volume += soup.find('issue').text
                volume += ')'
            volume += ' '
    except:
        volume = 'not found'
        
    try:
        page = ''
        if article.find('pagination'):
            if '-' in article.find('pagination').text:
                page = 'pp. '
                page_str = article.find('pagination').text
                page_str = page_str.strip('\n')
                page += page_str
                page += ' '
            else:
                page = 'p. '
                page_str = article.find('pagination').text
                page_str = page_str.strip('\n')
                page += page_str
                page += ' '
    except:
        page = 'not found'
    
    try:
        journal_title = ''
        if journal.find('title'):
            journal_title = journal.find('title').text
            journal_title += ' '

        JournalIssue = journal.find('journalissue')

        month = JournalIssue.find('month')
        date = ''
        if month:
            month = JournalIssue.find('month').text
            if len(month) < 3:
                month_int = int(str(month))
                month = calendar.month_abbr[month_int]

            year = JournalIssue.find('year').text
            date = '('
            date += month
            date += '. '
            date += year
            date += '). '
        elif JournalIssue.find('year'):
            date = '('
            date += JournalIssue.find('year').text
            date += '). '
        else:
            ''
    except:
        date = 'not found'
    
    try:
        pubmed = ''
        if soup.find('articleid'):
            pubmed = 'PUBMED: '
            pubmed += soup.find('articleid').text
            pubmed += '; '
            doi_pii = article.find_all('elocationid')
            doi_pii_str = ""
            if len(doi_pii) > 1:
                if 'doi' in str(doi_pii[0]):
                    doi_pii = doi_pii[0].text
                    doi_pii_str += "DOI "
                    doi_pii_str += doi_pii
                    doi_pii_str += "."
                elif 'doi' in str(doi_pii[1]):
                    doi_pii = doi_pii[1].text
                    doi_pii_str += "DOI "
                    doi_pii_str += doi_pii
                    doi_pii_str += "."
            elif len(doi_pii) == 1:
                if 'doi' in str(doi_pii[0]):
                    doi_pii = doi_pii[0].text
                    doi_pii_str += "DOI "
                    doi_pii_str += doi_pii
                    doi_pii_str += "."
                elif 'pii' in str(doi_pii[0]):
                    doi_pii = doi_pii[0].text
                    doi_pii_str += "PII "
                    doi_pii_str += doi_pii
                    doi_pii_str += "."
    except:
        doi_pii_str = 'not found'
    
    
    try:
        abstract = ''
        if article.find('abstracttext'):
            abstract = article.find('abstracttext').text
    except:
        abstract = 'not found'

    result = []
    result.append(authors)
    result.append(article_title)
    result.append(journal_title)
    result.append(volume)
    result.append(date)
    result.append(pubmed)
    result.append(doi_pii_str)
    result.append(abstract)

    return result


def get_doi(soup):
    '''
    Objective: Extracts all bibliography information
    '''
    article = soup.find('article')

    pubmed = ''
    if soup.find('articleid'):
        pubmed = 'PUBMED: '
        pubmed += soup.find('articleid').text
        pubmed += '; '
        doi_pii = article.find_all('elocationid')
        doi_pii_str = ""
        if len(doi_pii) > 1:
            if 'doi' in str(doi_pii[0]):
                doi_pii = doi_pii[0].text
                doi_pii_str += "DOI "
                doi_pii_str += doi_pii
                doi_pii_str += "."
            elif 'doi' in str(doi_pii[1]):
                doi_pii = doi_pii[1].text
                doi_pii_str += "DOI "
                doi_pii_str += doi_pii
                doi_pii_str += "."
        elif len(doi_pii) == 1:
            if 'doi' in str(doi_pii[0]):
                doi_pii = doi_pii[0].text
                doi_pii_str += "DOI "
                doi_pii_str += doi_pii
                doi_pii_str += "."
            elif 'pii' in str(doi_pii[0]):
                doi_pii = doi_pii[0].text
                doi_pii_str += "PII "
                doi_pii_str += doi_pii
                doi_pii_str += "."

        result = []
        result.append(pubmed)
        result.append(doi_pii_str)

        return result
    else:
        result = []
        result.append(pubmed)
        result.append(np.nan)


def simpletldf(text):
    # Tokenizing the text
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text)

    # Creating a frequency table to keep the
    # score of each word

    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    # Creating a dictionary to keep the score of each sentence
    sentences = sent_tokenize(text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]

    # Average value of a sentence from the original text

    average = int(sumValues / len(sentenceValue))

    # Storing sentences into our summary.
    summary = ''
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence
    print(summary)


#%%


# create pre-defined keyword lists and functions
list_of_pop = ['Human', "Adult", "People", "Monkey", "Primate", "Pig", "In vitro",
               "Hens", "Child", "Mice", "Rat", "Chicken", "Women", "Men", "Patients"]


# Get user input
# Ask for keywords of interest
#keyword = str(input('Please enter the keywords (replace spaces with +) '))
keywords = str(input('Please enter the keywords (replace spaces with +) '))

# Limit the number of results returned
num_results = int(input('Please enter the number of results '))

# add minimum and maximum search dates
MIN_DATE = str(input('Minimum Date (YYYY/MM/DD)'))
MAX_DATE = str(input('Maximum Date (YYYY/MM/DD)'))

# what level of detail:

doi_only = str(input(
    'Do you only want the DOI or do you want the paper information? If doi only, input yes otherwise more'))


# clean up elements in search url
# url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=NUM&sort=relevance&term=KEYWORDS"
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=NUM&sort=relevance&term=KEYWORDS&MIN_DATE=MIN_DATE&MAX_DATE=MAX_DATE"
url = url.replace('NUM', str(num_results))
url = url.replace('KEYWORDS', keywords)
url = url.replace('MIN_DATE', MIN_DATE)
url = url.replace('MAX_DATE', MAX_DATE)


# Get return results from pubmed json
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn’t verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn’t support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

webpage = urllib.request.urlopen(url).read()
dict_page = json.loads(webpage)
idlist = dict_page["esearchresult"]["idlist"]


articles_list = []

# We loop over each element in the idlist to get the soup and feed it into our function
print("Parsing")
for link in idlist:
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=idlist"
    url = url.replace('idlist', link)

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn’t verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn’t support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    if doi_only == "yes":
        article = get_doi(soup)
    else:
        article = get_bibliography(soup)
    articles_list.append(article)
    print('Pubmed ID: ', link)
print('Done!')

# Put scraped information into a dataframe and save as a csv
if doi_only == "yes":
    df = pd.DataFrame(articles_list)
    df.columns = ['pubmedID', 'doi']
else:
    df = pd.DataFrame(articles_list)
    df.columns = ['authors', 'articletitle', 'journal',
                  'volume', 'date', 'pubmedID', 'doi', 'abstract']
    df['Population'] = df['abstract'].apply(subpop)

file_name = keywords + '_' + str(num_results) + '.csv'
print("Filename", file_name)
df.to_csv(file_name)

print("Sneak peek:")
print(df.head())


#%%


# Get extra user arguments

customKeywordSearch = str(
    input("Name of your extra keyword category (If this is not relevant, type NA)"))

if customKeywordSearch == 'NA':
    print('Skipped')
    pass
else:
    #customKeywordSearchList = ast.literal_eval(sys.argv[1])
    customKeywordList = str(
        input("List all of the keywords (use comma between keywords or phrases)"))
    # convert string to list
    customKeywordList = list(customKeywordList.split(","))
    # remove trailing spaces
    customKeywordList = [x.strip() for x in customKeywordList]
    # create column for keywords
    df[customKeywordSearch] = df['abstract'].apply(subcustom)
    print("Added new column with custom search. ")
    print("Updated the file, new column is called: ", customKeywordSearch)
    df.to_csv(file_name)

    # second round:
    continueKeywordSearch = str(
        input("Would you like to add another keyword category (Type yes or no)"))

    if continueKeywordSearch == 'no':
        pass
    else:
        customKeywordSearch = str(input("Name of your extra keyword category"))
        customKeywordList = str(
            input("List all of the keywords (use comma between keywords or phrases)"))
        # convert string to list
        customKeywordList = list(customKeywordList.split(","))
        # remove trailing spaces
        customKeywordList = [x.strip() for x in customKeywordList]
        # create column for keywords
        df[customKeywordSearch] = df['abstract'].apply(subcustom)
        print("Added new column with custom search. ")
        print("Updated the file, new column is called: ", customKeywordSearch)
        df.to_csv(file_name)


tldr = str(input(
    "Would you like to a really simple TLDR based on the abstracts of all the papers (Type yes or no)"))

if tldr == 'yes':
    print(' ')
    print('TLDR based on all abstracts:')
    print(' ')
    simpletldf(df['abstract'].str.cat(sep=' '))
else:
    pass



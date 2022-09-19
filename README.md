# literature_review_scripts
Python scripts used to extract pdfs from pubmed and to extract and analyze text 

PubmedScraper.py:

Purpose of this script:

Allows users to define keywords (along with a given timeframe) for their Pubmed search. The script returns a pandas dataframe and csv file with the following information: 'authors', 'ArticleTitle', 'journal_title', 'volume', 'date', 'pubmed', 'doi_pii_str', 'abstract','population', 'symptoms', 'bacteria'.* Users can also add a custom column(s) as well. Note that * columns return a limited number of search terms.

Required input:

User defined keywords and date ranges

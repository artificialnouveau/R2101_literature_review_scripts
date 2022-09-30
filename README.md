# literature_review_scripts
Python scripts used to extract pdfs from pubmed and to extract and analyze text 

* PubmedScraper.py:

Purpose of this script:

Allows users to define keywords (along with a given timeframe) for their Pubmed search. The script returns a pandas dataframe and csv file with the following information: 'authors', 'ArticleTitle', 'journal_title', 'volume', 'date', 'pubmed', 'doi_pii_str', 'abstract','population', 'symptoms', 'bacteria'.* Users can also add a custom column(s) as well. Note that * columns return a limited number of search terms.

Required input:

User defined keywords and date ranges. Can be used in the terminal or in a python IDE

* Extract_key_sentences_from_scientific_pdf.py

Purpose of this script:

Allows users to download pdfs (based on dois) from scihub and to subsequently identify specific sentences that contain keywords of interest.

Required input:

.csv or .txt with DOIs, title, author, and year of papers of interest. Can be used in a python IDE

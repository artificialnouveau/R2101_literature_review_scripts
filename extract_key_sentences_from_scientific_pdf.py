#!/usr/bin/env python
# coding: utf-8

# Author name: Ahnjili
# Author git name: artificialnouveau
# Word of caution: 
#    1. This tool is not perfect! Please read through all of your papers for a thorough understanding of the literature
#    2. This tool downloads your papers from scihub. Not all papers will be available on scihub, so you may need to manually download the papers


#%%
#If you do not have scidownl then run the following command: 
#! pip install scidownl

#Import libraries 
import os
import pandas as pd
import numpy as np
import re
from scidownl import scihub_download
import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#%%
# User input required! 
# Provide a csv/text file that contains two columns a title (of the article name) and the doi
# For optimal results include Author and Year
os.chdir('C:/Users/AZhuparris/Documents/LiteratureReview/')
pdf_df= pd.read_csv('./test.csv')

#the title of the articles will become the filename of your pdfs. this step removes any punctuation and lowers the cases of your title
pdf_df['title'] = pdf_df['title'].apply(lambda x:re.sub(r'[^\w\s]','',x.rstrip().lstrip()))
pdf_df['title_clean'] = pdf_df['title'].str.replace(' ','_').str.lower()
pdf_df['title_clean'] = pdf_df['title_clean'].apply(lambda x:re.sub(r'[^\w\s]','',x.rstrip().lstrip()))

#the doi will be used to scrape the data from scihub. This step will make the doi string into an acceptable format
pdf_df['doi_clean']=pdf_df['doi'].apply(lambda x:str(x) if 'https://doi.org/' in str(x) else 'https://doi.org/'+str(x))
pdf_df['doi_clean']=np.where(pdf_df['doi_clean']=='https://doi.org/nan',np.nan,pdf_df['doi_clean'])


print('number of papers',pdf_df['doi'].nunique())
pdf_df.columns

#%%
# No user input required, just run the cell
# Download pdf from scihub and save into a folder called scihub
# this steps looks at all the pdfs already in the scihub folder (just in case you choose to run this step multiple times)

pdfs = os.listdir("./scihub/")
pdfs = [elem.replace('.pdf', '') for elem in pdfs]

paper_type='doi'
for i in range(0,len(pdf_df)):
    print(i)
    paper=pdf_df.iloc[i]["doi_clean"]
    print('title: ',pdf_df.iloc[i]["title"])
    out='./scihub/'+pdf_df.iloc[i]["title_clean"]+'.pdf'
    print(out)
    if pdf_df.iloc[i]["title_clean"] in pdfs:
        print('Already have this pdf')
    else:
        try:
            scihub_download(paper, paper_type=paper_type, out=out)
        except:
            print('could not download pdf')
    print(' ')



# this section checks which pdfs are missing.  If they are missing you will have to manually download them

count=0
for i in range(0,len(pdf_df)):
    if pdf_df.iloc[i]['title_clean'] not in pdfs:
        print(count)
        count+=1
        print('No pdf for')
        print(pdf_df.iloc[i]['title'])
        print(pdf_df.iloc[i]['title_clean'])
        print(' ')
    if count == 0 and i == len(pdf_df)-1:
        print('No pdfs are missing')



#%%
# No user input required, just run the cell
# Converted PDF file to txt format for better pre-processing

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

def convert_pdf_to_txt(path):
    #inspiration: https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python/26495057#26495057
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    text = text.strip('\n')
    text = text.replace('\n','')
    text = text.strip('\t')

    fp.close()
    device.close()
    retstr.close()
    return text


# Reads through the list of filenames provided in the pdf_df
for i in range(0,len(pdf_df)):
    print(i)
    filename ='./scihub/'+pdf_df.iloc[i]['title_clean']+'.pdf'
    print(filename)
    try:
        #finds the pdf and converts the text into a string into the text column of pdf_df
        text=convert_pdf_to_txt(filename)
        pdf_df.loc[i,'text']=text
        
    except:
        print('could not get text')
        print('==================')



#%% 
# Extracting Keywords

def find_sentence_one_text (text, string):
    text = re.sub(r'[0-9]', '', text.lower())
    textlist = text.split('.')
    res = [y for y in textlist if string in y]
    return res

def found_word(sentence, word_list):
    sentence_= sentence.lower()
    sentence_ = re.sub(r'[0-9]', '', sentence_)
    return any(word in word_list for word in sentence_.split())

def extract_key_sentences(text,word_list):
    list_sentences = []
    for sentence in text.split('.'):
        if found_word(sentence, word_list):
            list_sentences.append([sentence + '.'])
    if not list_sentences:
        list_sentences = np.nan
    return list_sentences

def print_lines(df,col_of_interest,include_reference=True):
    tempdf = df[['authors', 'year', 'title', col_of_interest]].dropna().reset_index()
    for i in range(0,len(tempdf)):
        print(tempdf.iloc[i]['title'])
        if include_reference:
            print(tempdf.iloc[i]['authors'].replace(";",",").split(',')[0])
            print(tempdf.iloc[i]['year'])
        print(' ')
        print(tempdf.iloc[i][col_of_interest])
        print('============================')
        print(' ')
            
#%%
# User input required

# Let's get ready to parse!
# use this if you want to find a specific work from one specific paper
find_sentence_one_text(pdf_df.iloc[0]['text'],'tremor')
find_sentence_one_text(pdf_df.iloc[0]['text'],'classification')


# create a list of keywords that you are interested in (all lower case)
keywords_list = ['random forest','regression','linear regression','logistic regression','neural network']

pdf_df['temp'] = pdf_df['text'].apply(lambda x : extract_key_sentences(str(x),keywords_list))
print_lines(pdf_df,'temp')

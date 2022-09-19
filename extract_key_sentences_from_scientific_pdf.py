# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 17:00:22 2022

@author: artificialnouveau
"""

#import libraries
import pandas as pd
import numpy as np
import re
from scidownl import scihub_download
import warnings
warnings.filterwarnings("ignore")

# import list of doi's 
df=pd.read_csv('./listofdoi.csv')
df['Title']= df['Title'].apply(lambda x:re.sub(r'[^\w\s]','',x.rstrip().lstrip()))
df['title_clean']=df['Title'].str.replace(' ','_').str.lower()
df['title_clean']= df['title_clean'].apply(lambda x:re.sub(r'[^\w\s]','',x.rstrip().lstrip()))
df['DOI_clean']=df['DOI'].apply(lambda x:str(x) if 'https://doi.org/' in str(x) else 'https://doi.org/'+str(x))
df['DOI_clean']=np.where(df['DOI_clean']=='https://doi.org/nan',np.nan,df['DOI_clean'])

# import PDFs from SciHub
paper_type='doi'
for i in range(0,len(df)):
    print(i)
    paper=df.iloc[i]["DOI_clean"]
    print('Title: ',df.iloc[i]["Title"])
    out='./scihub/'+df.iloc[i]["title_clean"]+'.pdf'
    print(out)
    try:
        scihub_download(paper, paper_type=paper_type, out=out)
    except:
        print('could not download pdf')
        
        
# convert pdfs to readable text
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

for i in range(0,len(df)):
    print(i)
    filename ='./scihub/'+df.iloc[i]['title_clean']+'.pdf'
    print(filename)
    try:
        text=convert_pdf_to_txt(filename)
        df.loc[i,'text']=text
        
    except:
        print('could not get text')
        print('==================')

# find sentences with keywords of interest
def found_word(sentence, word_list):
    return any(word in word_list for word in sentence.split())

def extract_key_sentences(text,word_list):
    list_sentences = []
    for sentence in text.split('.'):
        if found_word(sentence, word_list):
            list_sentences.append([sentence + '.'])
    return list_sentences

machine_learning_list=['machine learning', 'deep learning', 'artificial intelligence']
df['machine_learning_sentence']=df['text'].apply(lambda x : extract_key_sentences(str(x),machine_learning_list))


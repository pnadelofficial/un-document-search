import streamlit as st
import urllib.request
from zipfile import ZipFile
import os

def reset_pages():
    st.session_state['page_count'] = 0

@st.cache_data
def get_data():
    urllib.request.urlretrieve("https://tufts.box.com/shared/static/2q5ivxwmbyypz8yrjmpe1oyr89bbqvj7.csv", "un_data_final_chunks.csv")
    urllib.request.urlretrieve("https://tufts.box.com/shared/static/l1ux7ue4191migrq5l8dqxfayfycexa5.zip", "un_doc_search.zip")
    with ZipFile('un_doc_search.zip', 'r') as zip_ref:
        zip_ref.extractall('indexdir')
    # if not os.listdir('data'):
    #     urllib.request.urlretrieve("https://tufts.box.com/shared/static/t9cpmf2e57cwz0rtkbjew4usnopg78rd.csv", "data/chunked_press_review.csv") # need to update

    # if not os.listdir('indices'):
    #     # os.makedirs('indices/press_review_index', exist_ok=True)
    #     urllib.request.urlretrieve("https://tufts.box.com/shared/static/16rzcw8kmjlfyrhtkvbypqt4fh5ye8na.zip", "indices/hepc_index.zip")
    #     with ZipFile('indices/hepc_index.zip', 'r') as zip_ref:
    #         zip_ref.extractall('indices/press_review_index')
    #     # copy the index files to the correct directory
    #     # os.rename('indices/press_review_index/indices/press_review_index', 'indices/press_review_index/')
        
    print("**DEBUG**")
    print("Current Working Directory", os.getcwd())
    print("Files in indexdir:", os.listdir('indexdir'))
    print("Files in current directory:", os.listdir('.'))

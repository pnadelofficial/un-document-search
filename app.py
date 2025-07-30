import streamlit as st
import collections 

from simple_search.searcher import Searcher
from simple_search.dataloader import DataLoader
from simple_search.utils import reset_pages, get_data

st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="expanded", menu_items=None)

st.title('UN Document Search Search')

get_data()

if 'page_count' not in st.session_state:
    st.session_state['page_count'] = 0
if 'to_see' not in st.session_state:
    st.session_state['to_see'] = 10
if 'additional_context' not in st.session_state:
    st.session_state['additional_context'] = collections.defaultdict(str)

with st.expander('Click for further information on how to construct a query.'):
    st.markdown("""
    * If you'd like to search for just a single term, you can enter it in the box above. 
    * If you'd like to search for a phrase, you can enclose it in quotations, such as "Member States".
    * A query like "Member States"~5 would return results where "Member" and "States" are at most 5 words away from each other.
    * AND can be used as a boolean operator and will return results where two terms are both in a passage. AND is automatically placed in a query of two words, so Member States is internally represented as Member AND States.
    * OR can be used as a boolean operator and will return results where either one of two terms are in a passage.
    * NOT can be used as a boolean operator and will return results which do not include the term following the NOT.
    * From these boolean operators, one can construct complex queries like: peace AND Ukraine NOT "Crimea". This query would return results that have both peace and Ukraine in them, but do not have Crimea.
    * Parentheses can be used to group boolean statements. For example, the query Ukraine AND ("Russia" OR  "Crimea") would return results that have Ukraine and either Russia or Crimea in them. 
    * If you'd like to search in a specific date range, you can specify it with the date: field. For example, dates:[20210101 TO 20220101] Ukraine would return results between January 1st, 2021 and January 1st, 2022 that have Ukraine in them.
    """)

doc_type = st.radio('Choose a newspaper type', ['All', 'Security Council text', 'Meeting text'], on_change=reset_pages)

dataloader = DataLoader()
data, _ = dataloader.load()

query_str = st.text_input('Search for a word or phrase', on_change=reset_pages)
start_date = st.date_input("Start date", value=None, min_value="2000-01-01", max_value="2026-01-01")
end_date = st.date_input("End date", value=None, min_value="2000-01-01", max_value="2026-01-01")
topics = st.multiselect('Select topics', options=data.topics.unique().tolist())

default_context = st.number_input('How many sentences of context would you like to see by default?', min_value=0, max_value=10, value=0, step=1, help='This number represents the amount of sentences to be added before and after the result.', on_change=reset_pages)
to_see = st.number_input('How many results would you like to see per page?', min_value=1, max_value=100, value=10, step=1)
stemmer = st.toggle('Use stemming', help='If selected, the search will use stemming to find words with the same root. For example, "running" will match "run" and "ran".', on_change=reset_pages)

if query_str != '':
    if doc_type == "Security Council text":
        doc_type = 'Security Council'
    elif doc_type == "Meeting text":
        doc_type = 'Meeting'

    searcher = Searcher(
        query_str, 
        dataloader, 
        stemmer, 
        doc_type=doc_type,
        start_date=start_date,
        end_date=end_date,
        topic=topics,
        added_default_context=default_context
    )
    searcher.search(to_see)

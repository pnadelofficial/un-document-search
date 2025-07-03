import streamlit as st
from whoosh.qparser import QueryParser, query
from datetime import datetime
import gspread
from simple_search.exporter import Exporter
from simple_search.page import Page
from simple_search.dataloader import DataLoader

@st.cache_resource
def load_google_sheet():
    CREDS = st.secrets['gsp_secrets']['my_project_settings']
    gc = gspread.service_account_from_dict(CREDS)
    return gc.open('simple-search-feedback').sheet1 # gmail account

class Searcher:
    def __init__(self, query_str:str, dataloader:DataLoader, stemmer:bool, doc_type:str='All', start_date=None, end_date=None, topic=None, added_default_context:int=0) -> None:
        self.query_str = query_str
        self.dataloader = dataloader
        self.data, self.ix, = self.dataloader.load()
        self.stemmer = stemmer
        self.doc_type = doc_type
        self.start_date = start_date
        self.end_date = end_date
        self.topic = topic
        self.added_default_context = added_default_context
    
    def parse_query(self):
        if self.stemmer: 
            print("Using stemming")
            parser = QueryParser("chunk", self.ix.schema, termclass=query.Variations)
        else:
            parser = QueryParser("chunk", self.ix.schema)    
        
        if self.doc_type != 'All':
            doc_prepend = f"doc_type:[{self.doc_type}]"
            self.query_str = f"{doc_prepend} AND {self.query_str}"
        if self.start_date and self.end_date:
            date_prepend = f"date:[{self.start_date.strftime('%Y%m%d')} TO {self.end_date.strftime('%Y%m%d')}]"
            self.query_str = f"{date_prepend} AND {self.query_str}"
        if self.topic:
            if isinstance(self.topic, list):
                topics_str = ' OR '.join([f'topic:"{t}"' for t in self.topic])
                topic_prepend = f'topic:({topics_str})'
            else:
                topic_prepend = f'topic:"{self.topic}"'
            self.query_str = f"{topic_prepend} AND {self.query_str}"
        print(f"Query string: {self.query_str}")
        q = parser.parse(self.query_str)
        # all_tokens = list(set(self.query_str.split(' ') + [item for sublist in [variations(t) for t in self.query_str.split(' ')] for item in sublist]))
        searches = [q.lower() for q in self.query_str.split() if (q != 'AND') and (q != 'OR') and (q != 'NOT') and (q != 'TO')]
        
        return q, searches

    def search(self, to_see):
        q, searches = self.parse_query()
        with self.ix.searcher() as searcher:
            results = searcher.search(q, limit=None, sortedby="date")
            self.results = results
            default = 1
            
            doc_list = self.data.topics.unique().tolist()
            st.session_state['pages'] = [self.results[i:i + to_see] for i in range(0, len(self.results), to_see)]

            with st.sidebar:
                st.markdown("# Page Navigation")
                if st.button('See next page', key='next'):
                    st.session_state['page_count'] += 1
                if st.button('See previous page', key='prev'):
                    st.session_state['page_count'] -= 1   
                if (len(st.session_state['pages']) > 0):
                    page_swap = st.number_input('What page do you want to visit?', min_value=default, max_value=len(st.session_state['pages']), value=default)
                if st.button('Go to page'):
                    st.session_state['page_count'] = page_swap-1
                st.divider()
                st.markdown("# Export to PDF")
                if st.button('Export this page to PDF'):
                    e = Exporter(self.query_str)
                    e(self)
                if st.button('Export all results to PDF'):
                    e = Exporter(self.query_str, full=True)
                    e(self)
                st.divider()
                st.markdown("# Feedback")
                feedback = st.text_area('Give any feedback you may have here')
                fb = load_google_sheet()
                if st.button('Send feedback'):
                    fb.append_row([datetime.now().strftime("%m/%d/%Y"), feedback])
                
            st.write(f"There are **{len(self.results)}** results for this query.")
            st.divider()

            if (default == 0) or (len(self.results) == 0):
                pass
            else:
                if len(doc_list) > 0:
                    p = Page(st.session_state['pages'][st.session_state['page_count']], self.data, searches, doc_list, added_default_context=self.added_default_context)
                    p()

                    st.write(f"Page: {st.session_state['page_count']+1} out of {len(st.session_state['pages'])}")
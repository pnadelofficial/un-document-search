import streamlit as st
from string import punctuation
import re
from whoosh.searching import Results 
import pandas as pd
from typing import List

class Page:
    def __init__(self, results:Results, data:pd.DataFrame, searches:List, doc_search:List, display_date:bool=True, added_default_context:int=0) -> None:
        self.results = results
        self.data = data
        self.searches = searches
        self.doc_search = doc_search
        self.display_date = display_date
        self.added_default_context = added_default_context

    def escape_markdown(self, text):
        '''Removes characters which have specific meanings in markdown'''
        MD_SPECIAL_CHARS = "\`*_{}#+"
        for char in MD_SPECIAL_CHARS:
            text = text.replace(char, '').replace('\t', '')
        return text
    
    def no_punct(self, word):
        '''Util for below to remove punctuation'''
        return ''.join([letter for letter in word if letter not in punctuation.replace('-', '') + '’' + '‘' + '“' + '”' + '—' + '…' + '–' + '-']) 
    
    def no_digits(self, word):
        '''Util for below to remove digits'''
        return ''.join([letter for letter in word if not letter.isdigit()])

    def remove_tilde(self, word):
        return re.sub('~\d+', '', word)

    def inject_highlights(self, text, searches):
        '''Highlights words from the search query''' 
        searches = [self.remove_tilde(s).replace('"', '') for s in searches if s != '']
        esc = punctuation + '."' + '..."'
        inject = f"""
            <p>
            {' '.join([f"<span style='background-color:#fdd835'>{word}</span>" if (self.no_digits(self.no_punct(word.lower())) in searches) and (word not in esc) else word for word in text.split()])}
            </p>
            """ 
        return inject 

    def add_context(self, data:pd.DataFrame, r, amount=1):
        sents = []
        res_idx = int(data.loc[data.chunks.str.contains(r['chunk'], regex=False, na=False)].index[0])
        after_mask = (data.index >= res_idx) & (data.index < res_idx + amount + 1) & (data.topics == r['topic'])
        before_mask = (data.index < res_idx) & (data.index >= res_idx - amount) & (data.topics == r['topic'])
        sents += list(data.loc[before_mask, 'chunks'])
        sents += list(data.loc[after_mask, 'chunks'])
        return '\n'.join(sents)

    def check_metadata(self, r, data, display_date):
        keys = list(r.keys())
        # title
        st.markdown(f"<small><b>Document topic: {r['topic']}</b></small>", unsafe_allow_html=True)
        st.markdown(f"<small><b>Document origin: {r['doc_type']}</b></small>", unsafe_allow_html=True)
        
        # date
        if display_date and ('date' in keys) and (re.match('\d', str(r['date']))): 
            st.markdown(f"<small><b>Date: {r['date']}</b></small>", unsafe_allow_html=True)
        elif display_date and ('date' in keys) and (not re.match('\d', str(r['date']))):
            st.markdown("<small><b>Date: No date found</b></small>", unsafe_allow_html=True)
        elif display_date and ('date_possible' in keys) and (re.match('\d', r['date_possible'])):
            st.markdown(f"<small><b>Date: {r['date_possible']}</b></small>", unsafe_allow_html=True)
        elif display_date and ('date_possible' in keys) and (not re.match('\d', r['date_possible'])):
            st.markdown("<small><b>Possible Date: No date found</b></small>", unsafe_allow_html=True)
        else:
            st.markdown("<small><b>Date: No date found</b></small>", unsafe_allow_html=True)

    def display_results(self, i, r, data, searches, added_default_context=0, display_date=True, text_return=True):
        self.check_metadata(r, data, display_date)
        full = self.add_context(data, r, added_default_context)
        if (st.session_state['additional_context'][i] == '') or (len(st.session_state['additional_context'][i]) < len(full)):
            st.session_state['additional_context'][i] = full
        amount = st.number_input('Choose context length', key=f'num_{i}', value=1, step=1, help='This number represents the amount of sentences to be added before and after the result.')
        if st.button('Add context', key=f'con_{i}'):
            full = self.add_context(data, r, amount)
            if (st.session_state['additional_context'][i] == '') or (len(st.session_state['additional_context'][i]) < len(full)):
                st.session_state['additional_context'][i] = full
        st.markdown(self.inject_highlights(self.escape_markdown(full.replace('\n --', ' --')), searches), unsafe_allow_html=True) 
        st.markdown("<hr style='width: 75%;margin: auto;'>", unsafe_allow_html=True)
        if text_return:
            return full, r 

    def __call__(self):
        for i, r in enumerate(self.results):
            if r['topic'] in self.doc_search:
                self.display_results(i, r, self.data, self.searches, self.added_default_context, display_date=self.display_date)
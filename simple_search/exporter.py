import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

class Exporter:
    def __init__(self, query_str:str, full:bool=False):
        self.query_str = query_str
        self.full = full

    def pdf_set_up(self):
        self.status = st.empty()
        self.status.info('Generating PDF, please wait...')

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', './fonts/DejaVuSansCondensed.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', './fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
        pdf.set_font('DejaVu', 'B', 12)
        
        self.row_height = pdf.font_size
        pdf.multi_cell(0, self.row_height*3, f"Search Query: {self.query_str}", 1)
        pdf.ln(self.row_height*3)

        self.pdf = pdf

        self.col_width = pdf.w / 1.11
        self.spacing = 1.5

    def fill_pdf(self, searcher_object):
        if self.full:
            with searcher_object.ix.searcher():
                for r in searcher_object.results:
                    text = r['chunks'].replace("<br>", '')
                    self.pdf.set_font('DejaVu', 'B', 12)
                    topic = r['topic']
                    self.pdf.multi_cell(self.col_width, self.row_height*self.spacing, f"Topic: {topic}", 0, ln=2)
                    self.pdf.multi_cell(self.col_width, self.row_height*self.spacing, f"Date: {datetime.strftime(r['date'], '%B %-d, %Y')}", 0, ln=2)
                    self.pdf.set_font('DejaVu', '', 14)
                    self.pdf.multi_cell(self.col_width, self.row_height*self.spacing, text, 'B', ln=2)
                    self.pdf.ln(self.row_height * self.spacing)
        else:
            page = st.session_state['pages'][st.session_state['page_count']]
            additional_context_dict = {}
            for i in range(len(page)):
                if (page[i]['chunk'] != st.session_state['additional_context'][i]) or (not st.session_state['additional_context'][i] == ''):
                    additional_context_dict[i] = {'text':st.session_state['additional_context'][i]} | {k:page[i][k] for k in page[i].keys() if k != 'text'} 
                else:
                    additional_context_dict[i] = {k:page[i][k] for k in page[i].keys()}           
            for r in additional_context_dict.values():
                text = r['text'].replace("<br>", '')
                self.pdf.set_font('DejaVu', 'B', 12)
                topic = r['topic']
                self.pdf.multi_cell(self.col_width, self.row_height*self.spacing, f"Topic: {topic}", 0, ln=2)
                self.pdf.multi_cell(self.col_width, self.row_height*self.spacing, f"Date: {r['date']}", 0, ln=2)
                self.pdf.set_font('DejaVu', '', 14)
                self.pdf.multi_cell(self.col_width, self.row_height*self.spacing, text, 'B', ln=2)
                self.pdf.ln(self.row_height * self.spacing)
                
    def create_download_link(self, val, filename):
        b64 = base64.b64encode(val)
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

    def pdf_finish(self):
        n = datetime.now()
        query_str_for_file = self.query_str.replace(' ', '_').replace('"','').replace("'",'')
        html = self.create_download_link(self.pdf.output(dest="S"), f"search_results_{query_str_for_file}_{datetime.strftime(n, '%m_%d_%y')}")
        self.status.success('PDF Finished! Download with the link below.')
        st.markdown(html, unsafe_allow_html=True)
    
    def __call__(self, searcher_object):
        self.pdf_set_up()
        self.fill_pdf(searcher_object)
        self.pdf_finish()
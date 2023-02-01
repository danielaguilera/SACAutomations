from fpdf import FPDF
from datetime import datetime

class Exporter:
    def __init__(self):
        self.pdf = FPDF('P', 'mm', 'Letter')

    def make_pdf(self, name: str):
        self.pdf.add_page()
        self.pdf.set_font('helvetica', '', 16)
        self.pdf.set_text_color(0, 0, 205)
        self.pdf.set_xy(150,0)
        self.pdf.cell(40, 10, name)
        self.pdf.output(f'{name}.pdf')
    
    

    

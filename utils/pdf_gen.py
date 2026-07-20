import markdown
from fpdf import FPDF
import io

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "Blinkit Category Exploration - Insights Report", border=False, align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf_from_md(md_text):
    # Convert Markdown to HTML
    html_text = markdown.markdown(md_text)
    
    # fpdf2 supports writing basic HTML
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    
    # Write HTML to PDF
    pdf.write_html(html_text)
    
    # Return as bytes instead of bytearray
    return bytes(pdf.output(dest='S'))

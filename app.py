import os
import traceback
from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
from docx import Document
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)
CORS(app)

# 100% محفوظ پرانا روٹ
@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    pdf_path = 'temp.pdf'
    docx_path = 'temp.docx'
    
    file.save(pdf_path)
    
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()
    
    return send_file(docx_path, as_attachment=True)

# ورڈ سے پی ڈی ایف (ٹیبلز سمیت مکمل سپورٹ)
@app.route('/convert-word', methods=['POST'])
def convert_word_to_pdf():
    try:
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        filename_base = os.path.splitext(file.filename)[0]
        docx_path = f"temp_{filename_base}.docx"
        pdf_path = f"temp_{filename_base}.pdf"
        
        file.save(docx_path)
        
        doc = Document(docx_path)
        pdf_doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=letter,
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        normal_style.fontSize = 9
        normal_style.leading = 11

        # ٹیبل کے اندر ٹیکسٹ کے لیے چھوٹا اسٹائل
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=normal_style,
            fontSize=8,
            leading=10
        )
        
        story = []
        
        # ورڈ کے عناصر (پیراگراف اور ٹیبلز) کو ان کی ترتیب سے ریڈ کرنا
        for child in doc.element.body:
            if child.tag.endswith('p'):
                p = DocxParagraph(child, doc)
                if p.text.strip():
                    story.append(Paragraph(p.text, normal_style))
                    story.append(Spacer(1, 6))
                    
            elif child.tag.endswith('tbl'):
                table = DocxTable(child, doc)
                table_data = []
                
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        # سیل کے اندر موجود پیراگراف کا ٹیکسٹ نکالنا تاکہ فارمیٹنگ نہ بگڑے
                        cell_text = "\n".join([p.text.strip() for p in cell.paragraphs if p.text.strip()])
                        row_data.append(Paragraph(cell_text, table_cell_style))
                    table_data.append(row_data)
                
                if table_data:
                    # لیٹر پیج کے حساب سے ٹیبل کی چوڑائی (کل سائز ~550 ہے)
                    col_widths = [50, 250, 60, 90, 100] # ضرورت کے مطابق آٹومیٹک ایڈجस्टٹ
                    
                    t = Table(table_data)
                    t.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#4A5568')),
                        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')), # ہیڈر رو کا کلر
                        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                        ('TOPPADDING', (0,0), (-1,-1), 4),
                        ('LEFTPADDING', (0,0), (-1,-1), 4),
                        ('RIGHTPADDING', (0,0), (-1,-1), 4),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 8))
            
        pdf_doc.build(story)
        
        if os.path.exists(pdf_path):
            response = send_file(pdf_path, as_attachment=True, download_name=f"{filename_base}.pdf")
            return response
        else:
            return "PDF generation failed", 500
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(error_details)
        return f"Conversion Error: {str(e)}\n{error_details}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

import os
import traceback
from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)
CORS(app)

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
        pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # ورڈ فائل کے اندر موجود پیراگراف اور ٹیبلز کو ان کی اصل ترتیب (Order) کے ساتھ نکالنا
        for child in doc.element.body:
            if child.tag.endswith('p'):
                p = DocxParagraph(child, doc)
                if p.text.strip():
                    story.append(Paragraph(p.text, styles['Normal']))
                    story.append(Spacer(1, 8))
            elif child.tag.endswith('tbl'):
                table = DocxTable(child, doc)
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)
                
                if table_data:
                    t = Table(table_data)
                    t.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 10))
            
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

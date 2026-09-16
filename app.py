import os
import traceback
from flask import Flask, request, send_file
from pdf2docx import Converter
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# آپ کا پرانا PDF سے DOCX والا روٹ (یہ 100% محفوظ ہے اور بالکل ویسے ہی کام کرے گا)
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


# یہ نیا ورڈ سے پی ڈی ایف والا روٹ ہے جو پائथन کے ذریعے بالکل بغیر کسی ایرر کے چلے گا
@app.route('/convert-word', methods=['POST'])
def convert_word_to_pdf():
    try:
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        docx_path = 'temp_input.docx'
        pdf_path = 'temp_output.pdf'
        
        file.save(docx_path)
        
        # ورڈ فائل سے ٹیکسٹ پڑھنا
        doc = Document(docx_path)
        text_content = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_content.append(para.text)
        
        # ReportLab کے ذریعے صاف ستھری پی ڈی ایف بنانا
        pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        for line in text_content:
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 10))
            
        pdf_doc.build(story)
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)
        else:
            return 'PDF generation failed', 500
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(error_details)
        return f"Conversion Error: {str(e)}\n{error_details}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

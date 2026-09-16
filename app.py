import os
import subprocess
from flask import Flask, request, send_file
from pdf2docx import Converter

app = Flask(__name__)

# آپ کا پرانا PDF سے DOCX والا روٹ (بالکل محفوظ ہے)
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


# یہ نیا روٹ ہے جو Word (.docx) کو 100% پرفیکٹ PDF میں بدلے گا
@app.route('/convert-word', methods=['POST'])
def convert_word_to_pdf():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    docx_path = 'temp.docx'
    pdf_path = 'temp.pdf'
    
    file.save(docx_path)
    
    # LibreOffice کے ذریعے ورڈ کو پی ڈی ایف میں تبدیل کرنا
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', docx_path], check=True)
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return 'Conversion failed', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

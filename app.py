import os
import subprocess
import traceback
from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter

app = Flask(__name__)
CORS(app)

# 100% محفوظ پرانا روٹ (PDF سے Word)
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


# Word سے PDF والا روٹ (LibreOffice کے ذریعے 100% پرفیکٹ ٹیبلز اور تصاویر کے ساتھ)
@app.route('/convert-word', methods=['POST'])
def convert_word_to_pdf():
    try:
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        filename_base = os.path.splitext(file.filename)[0]
        docx_path = f"temp_{filename_base}.docx"
        output_dir = "/tmp"
        pdf_path = os.path.join(output_dir, f"{filename_base}.pdf")
        
        file.save(docx_path)
        
        # LibreOffice کے ذریعے ورڈ کو پی ڈی ایف میں بدلنے کی کمانڈ
        cmd = ["soffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, docx_path]
        subprocess.run(cmd, check=True)
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name=f"{filename_base}.pdf")
        else:
            return "PDF generation failed", 500
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(error_details)
        return f"Conversion Error: {str(e)}\n{error_details}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

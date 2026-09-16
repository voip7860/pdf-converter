import os
import shutil
import subprocess
import traceback
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


# ورڈ سے پی ڈی ایف والا روٹ (پاتھ چیکنگ کے ساتھ)
@app.route('/convert-word', methods=['POST'])
def convert_word_to_pdf():
    try:
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        docx_path = 'temp.docx'
        pdf_path = 'temp.pdf'
        
        file.save(docx_path)
        
        # چیک کریں کہ کیا سرور پر libreoffice یا soffice موجود ہے؟
        soffice_bin = shutil.which('soffice') or shutil.which('libreoffice')
        
        if not soffice_bin:
            return "Error: LibreOffice/Soffice is not installed or found in Render PATH. Please check Aptfile.", 500
        
        # ملنے پر کمانڈ چلائیں
        cmd = [soffice_bin, '--headless', '--convert-to', 'pdf', docx_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"LibreOffice execution failed: {result.stderr}", 500
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)
        else:
            return "PDF file was not generated", 500
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(error_details)
        return f"Conversion Error: {str(e)}\n{error_details}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

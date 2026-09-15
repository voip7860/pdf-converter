import os
from flask import Flask, request, send_file
from pdf2docx import Converter

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import os
import urllib.request
from pyresparser import ResumeParser
import nltk
import spacy


spacy.load('en_core_web_sm')

UPLOAD_FOLDER = './files/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['pdf'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():
	print(request.files)
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#OCR Engine 
		data = ResumeParser(app.config['UPLOAD_FOLDER']+filename).get_extracted_data()

		resp = jsonify(data)

		resp.status_code = 201
		return resp

	else:
		resp = jsonify({'message' : 'Allowed file types are pdf'})
		resp.status_code = 400
		return resp











if __name__ == '__main__':
    app.run(debug=True)




    


    

    



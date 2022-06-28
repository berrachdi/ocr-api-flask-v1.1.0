from flask import Flask, request, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import urllib.request
from pyresparser import ResumeParser
import nltk
import spacy
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_swagger_ui import get_swaggerui_blueprint



spacy.load('en_core_web_sm')

UPLOAD_FOLDER = './files/'

app = Flask(__name__)

# Config MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@127.0.0.1:3306/imagine_ocr_db"

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# swagger config
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(
	SWAGGER_URL,
	API_URL,
	config={
		'app_name':'OCR Engine service'
	}

)

app.register_blueprint(SWAGGER_BLUEPRINT,url_prefix = SWAGGER_URL)

ALLOWED_EXTENSIONS = set(['pdf'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize the database
db = SQLAlchemy(app)
# Create a model
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(200))
    skills =  db.Column(db.String(1000))
    expertise = db.Column(db.String(1000))
    formation =  db.Column(db.String(1000))
    phone =  db.Column(db.String(20))
    fullName =  db.Column(db.String(100))
    address =   db.Column(db.String(200))
    def __repr__(self):
        return '<User {}>'.format(self.email)

# data boucle
def exctract_data(items):
    if items is None:
        return ""
    else:
        return ' '.join([str(item) for item in items])

#swagger endpoint






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

		

		# Save data in MySQL Database
		user = Users(

            email=data['email'],
            fullName = data['name'],
            address = "",
            skills = exctract_data(data['skills']),
            expertise = exctract_data(data['experience']),
            formation = exctract_data(data['degree']),
            phone = data['mobile_number']

        )
		db.session.add(user)
		db.session.commit()
		db.session.close()
        
		resp = jsonify(data)
		resp.status_code = 201
		return resp

	else:
		resp = jsonify({'message' : 'Allowed file types are pdf'})
		resp.status_code = 400
		return resp











if __name__ == '__main__':
    app.run(debug=True)




    


    

    



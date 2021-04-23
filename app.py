import os
from flask import Flask, flash, session, request, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# set secret key
app.config['SECRET_KEY'] = 'b539918b62de0c23a4032445'

# configure upload folder
upload_folder = './uploads'
app.config['UPLOAD_FOLDER'] = upload_folder
# app.use_x_sendfile = True

# configure stems folder
stems_folder = './stems'
app.config['STEMS_FOLDER'] = stems_folder

env = "prod"

# configure database

if env == "dev":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_user:test_user@localhost:5432/upload'
    app.config['SQLALCHEMY_BINDS'] = {
        'feedback': 'postgresql://test_user:test_user@localhost:5432/feedback',
    }
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hcdbzidojphhrg:4a3f391965e44e08583f8c66ab3b4a2fca8be39543bbf8814aeeaff3f62297e7@ec2-34-230-167-186.compute-1.amazonaws.com:5432/dftm9jubu7nks0'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# create upload model
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "ID: {}, FILENAME: {}, DATE_POSTED: {}".format(str(id), filename, str(date_posted))

# create feedback model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "ID: {}, EMAIL: {}, MESSAGE: {}, DATE_POSTED: {}".format(str(id), filename, message, str(date_posted))

def allowed_file(filename):
    allowed_extensions = {'mp3', 'wav'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def separate(filename):
    from spleeter.separator import Separator
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['STEMS_FOLDER']))
    return None

def return_file(filename):

    split_filename = filename.split('.')
    file_name = split_filename[0]
    path = file_name + ".zip"
    return path

def create_zip(filename):
    from zipfile import ZipFile

    split_filename = filename.split('.')
    file_name = split_filename[0]
    zipfile_name = "./zip/" + file_name + ".zip"

    vocals_path = './stems/' + file_name + '/vocals.wav'
    instr_path = './stems/' + file_name + '/accompaniment.wav'

    zip_obj = ZipFile(zipfile_name, 'w')
    zip_obj.write(vocals_path)
    zip_obj.write(instr_path)

    zip_obj.close()

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('./zip', filename, as_attachment=True)

@app.route('/pro', methods=['GET', 'POST'])
def pro():
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')

        filename_to_feedback_db = Feedback(email=email, message=message)

        db.session.add(filename_to_feedback_db)
        db.session.commit()

        return render_template("pro.html")
    else:
        return render_template("pro.html")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # check if the post request has a file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        # if file exists then assign it to variable
        file = request.files['file']

        # check if the file has an empty name
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file exists and name checks out
        # start separation process
        if file and allowed_file(file.filename):

            # safely assign filename
            filename = secure_filename(file.filename)

            # save uploaded filename to database
            filename_to_upload_db = Upload(filename=filename)
            db.session.add(filename_to_upload_db)
            db.session.commit()

            # save file to the uploads folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # separate stems
            separate(filename)

            # create and return zip file
            create_zip(filename)
            zip_filepath = return_file(filename)

            relative_fp = "/download/" + zip_filepath

            return render_template("download.html", filename=relative_fp, zipfile_name=zip_filepath)
    else:
        return render_template("index.html")

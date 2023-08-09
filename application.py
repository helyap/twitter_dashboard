from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
import boto3
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import sys

sys.path.append('../')
# import os
# twint_search = os.system("python ../twint_search.py")
# database = os.system("python ../database.py")
import twint_search, database


UPLOAD_FOLDER = '../'
ALLOWED_EXTENSIONS = {'json'}

# app = Flask(__name__)

# Create an instance of Flask class (represents our application)
# Pass in name of application's module (__name__ evaluates to current module name)
app = Flask(__name__)
application = app # AWS EB requires it to be called "application"
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# on EC2, needs to know region name as well; no config
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# table = dynamodb.Table('books')

# Provide a landing page with some documentation on how to use API
@app.route("/")
def home():
    return render_template('index.html')

# Provide a landing page with some documentation on how to use API
@app.route("/search", methods = ["GET","POST"])
def search():
    if request.method == "POST":
        param_dict = {}
        param_dict['keyword'] = request.form['keyword']
        param_dict['since'] = request.form['before_time']
        param_dict['until'] = request.form['after_time']
        param_dict['limit'] = request.form['num_tweets']
        twint_search.search_tweet(param_dict)

    return render_template('search.html')

# Provide a landing page with some documentation on how to use API
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        keyword = request.form['keyword']
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            print(filename)
            database.send_data(filename, keyword, file=True)

    return render_template('upload.html')

if __name__ == "__main__":
    application.run()

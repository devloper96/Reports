import os
from flask import Flask, request, redirect, url_for ,Response, render_template, jsonify
from werkzeug import secure_filename
from azure.storage.blob import BlobService
import string
import random
import requests, json
import unicodedata
from pymongo import MongoClient
import JSONEncoder
import ast


blob_service = BlobService(account_name='manthan', account_key='q6+oDMKpKUyYe4aWuICSYL+APQZlTvJzgChEq8py72F2aek6SV3wKAL7445Tw9t0FLdHF0LUXn/ja17w7kwCgQ==')
blob_service.create_container('reports', x_ms_blob_public_access='container')


UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['jpeg','png',"jpg"])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fileextension = filename.rsplit('.',1)[1]
            print fileextension
            Randomfilename = id_generator()
            filename = Randomfilename + '.' + fileextension
            print filename
            blob_service=initilizeAzure()
            print "init"
            try:
                blob_service.put_block_blob_from_file(
                'reports',
                filename,
                file,
                )
            except Exception:
                print 'Exception=' + Exception 
                pass
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], Randomfilename + '.' + fileextension))
            ref =  'http://manthan.blob.core.windows.net/reports/' + filename
            apikey = "c574fc2c-2acb-448d-a83d-4a2573a3c943"
            url = 'https://api.havenondemand.com/1/api/sync/ocrdocument/v1?url=' + ref + '&apikey='+apikey
            r = requests.get(url)
            rtext=r.text
            rtext=unicodedata.normalize('NFKD', rtext).encode('ascii','ignore')
            text=str(rtext)
            keys = ["haemoglobin","rbc","wbc","neutrophils","lymphocytes","eosinophils","monocytes","basophills","platelets","m.c.v","m.c.h","m.c.h.c","h.c.t","rdw-sd"]
            keyalternative = {"rbc":["r.b.c","r.e.c"],"wbc":["wec","w.e.c"]}
            text = text.lower()
            value = []
            FinalResult = {}
            for k in keys:
                if k in text:
                    cnt=text.find(k)
                    while ord(str(text[cnt])) > 58 or ord(str(text[cnt])) < 47:
                        cnt += 1        
                    start = cnt
                    while ord(str(text[cnt])) < 58 and ord(str(text[cnt])) > 45:
                        cnt += 1
                    end = cnt

                    for t in range(start, end):
                        value.append(text[t])

                else:
                    for ka in keyalternative[k]:
                        if ka in text:
                            cnt=text.find(k)
                            while ord(str(text[cnt])) > 58 or ord(str(text[cnt])) < 47:
                                cnt += 1        
                            start = cnt
                            while ord(str(text[cnt])) < 58 and ord(str(text[cnt])) > 45:
                                cnt += 1
                            end = cnt

                            for t in range(start, end):
                                value.append(text[t])
                FinalResult[k]="".join(map(str, value))
                value=[]
            FinalResult["MobileNo"]=request.form["PhoneNo"]
            client = MongoClient()
            db = client.reports
            FinalResult=str(FinalResult).replace('.','')
            FinalResult=ast.literal_eval(FinalResult)
            response=db.reports.insert(FinalResult)
            return str(FinalResult)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file required>
        <input type=text name='PhoneNo' required>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/getReports/<MobileNo>')
def getByMobileNo(MobileNo):
    client = MongoClient()
    db = client.reports
    response=db.reports.find({"PhoneNo":MobileNo})
    return str(response)
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def initilizeAzure():
        blob_service = BlobService(account_name='manthan', account_key='q6+oDMKpKUyYe4aWuICSYL+APQZlTvJzgChEq8py72F2aek6SV3wKAL7445Tw9t0FLdHF0LUXn/ja17w7kwCgQ==')
        print "blob init"
        blob_service.create_container('reports', x_ms_blob_public_access='container')
        print "blob did"
        return blob_service


app.run(debug=True)


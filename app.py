import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from azure.storage.blob import BlobService
import string
import random


blob_service = BlobService(account_name='manthan', account_key='q6+oDMKpKUyYe4aWuICSYL+APQZlTvJzgChEq8py72F2aek6SV3wKAL7445Tw9t0FLdHF0LUXn/ja17w7kwCgQ==')
blob_service.create_container('reports', x_ms_blob_public_access='container')



UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['jpeg','png'])

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
            return 'manthan.blob.core.windows.net/reports/' + filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def initilizeAzure():
        blob_service = BlobService(account_name='manthan', account_key='q6+oDMKpKUyYe4aWuICSYL+APQZlTvJzgChEq8py72F2aek6SV3wKAL7445Tw9t0FLdHF0LUXn/ja17w7kwCgQ==')
        print "blob init"
        blob_service.create_container('reports', x_ms_blob_public_access='container')
        print "blob did"
        return blob_service


app.run()

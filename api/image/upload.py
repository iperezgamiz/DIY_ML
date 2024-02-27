from flask import request
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os

UPLOAD_FOLDER = 'imageuploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

parser = reqparse.RequestParser()
parser.add_argument('files', type=FileStorage, location='files', action='append')
parser.add_argument('labels', type=str, location='form', action='append')

def allowed_file(filename):
    return filename[-3:] in ALLOWED_EXTENSIONS


class UploadImages(Resource):
    def post(self, project_id):
        args = parser.parse_args()  
        file_names = args['files']  
        labels = args['labels']
        
        if not file_names:
            return {'code': 400, 'error': 'No files uploaded'}
        
        if len(file_names) != len(labels):
            return {'code': 400, 'error': 'Number of files and labels do not match'}
        
        for file, label in zip(file_names, labels):
            if not file:
                return {'code': 400, 'error': f'File not found in request for label: {label}'}
            filename = secure_filename(file.filename)
            if not allowed_file(filename):
                return {'code': 400, 'error': 'File type not allowed'}
    
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(file_path)
        
        return {'success': True}

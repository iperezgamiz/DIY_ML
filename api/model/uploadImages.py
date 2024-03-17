import tempfile
import os
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from mega import Mega
import redis
from flask import session, redirect

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

uploadImages_args = reqparse.RequestParser()
uploadImages_args.add_argument('dataset', location='files', type=FileStorage, required=True)

# MEGA access credentials
EMAIL = 'ec530storage@gmail.com'
PASSWORD = 'Txuleton99'

# Log in to MEGA
mega = Mega()
m = mega.login(EMAIL, PASSWORD)


class UploadImages(Resource):

    def post(self, model_id):
        args = uploadImages_args.parse_args()
        file_storage = args['dataset']

        # Save the uploaded file to a temporary location
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_storage.filename)
        file_storage.save(temp_file_path)

        # Specify the MEGA folder to upload the file
        mega_folder_name = f'{session["username"]}/{model_id}'

        # Find or create the MEGA folder to upload the file
        folder = m.find(mega_folder_name)
        if not folder:
            # Folder does not exist, create it
            folder = m.create_folder(mega_folder_name)
        else:
            # Folder exists, use the first one found
            folder = folder[0]

        # Upload the file to MEGA
        m.upload(temp_file_path, dest=folder)

        # Clean up the temporary file
        os.remove(temp_file_path)

        redis_db.hset("model:"+model_id, "dataset_location", mega_folder_name)
        redis_db.hset("model:"+model_id, "dataset_name", file_storage.filename)

        return redirect(f"/model/{model_id}/trainModel")

from __future__ import print_function
from flask import Flask, request, jsonify, session, after_this_request, render_template
from flask_session import Session
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import base64
from main_script import MainScript
import os
import traceback
from datetime import timedelta
import time

import sys
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address




# Define the path for storing training data
training_data_path = os.path.join(os.getcwd(), "training_the_model")
os.makedirs(training_data_path, exist_ok=True)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 4096 * 4096  # 16 MB
app.secret_key = os.urandom(24)

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5) 
Session(app)

limiter = Limiter(
    app= app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


# Configure CORS
CORS(app, supports_credentials=True)

dir_path = os.path.dirname(os.path.realpath(__file__))


main_script = MainScript()

def encode_image_to_base64(img_array):
    _, img_encoded = cv2.imencode('.png', img_array)
    img_bytes = img_encoded.tobytes()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64

def cleanup_old_sessions():
    session_dir = f'{dir_path}/flask_session'
    current_time = time.time()
    session_lifetime = app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()

    for filename in os.listdir(session_dir):
        file_path = os.path.join(session_dir, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > session_lifetime:
                os.remove(file_path)

@app.route('/initiate', methods=['POST'])
def initiate():
    print("Intiating")
    if 'image' not in request.files or 'base_coordinates' not in request.form:
        return jsonify({'error': 'Image or base coordinates not provided'}), 400

    file = request.files['image']
    base_coordinates = request.form['base_coordinates']
    base_coordinates = tuple(map(int, base_coordinates.split(',')))  # Convert to tuple of ints

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        image = Image.open(file)
        # img_array = np.array(image)

        # Store data in session
        # session['image_list'] = img_array.tolist()  # Convert numpy array to list for JSON serialization
        session['image'] = image

        img_with_preds, img_with_final_base, final_base_coords = main_script.initiate(np.array(image), base_coordinates)
        # final_base_coords = base_coordinates
        print('box_preds',main_script.box_preds)
        model_prediction_accepted = main_script.detection_logic.bot_error_accepted
        print('is_error_accepted:',model_prediction_accepted)

        if not model_prediction_accepted:
            print("Model prediction wasn't accepted. The data is being saved.", file=sys.stdout)
            main_script.save_user_input_for_model_training(training_data_path,final_base_coords,image)
        else:
            print("Model prediction was accepted. The data is not going to be saved.", file=sys.stdout)
        # final_base_coords = base_coordinates
        session['base_coordinates'] = final_base_coords

        image_scaler_fov = main_script.get_scale_of_image_fov(image, base_coordinates)

        if image_scaler_fov:
            session['image_scaler'] = image_scaler_fov

        response = {
            'got_scale': image_scaler_fov is not None,
            'model_predicted_correctly': model_prediction_accepted,
            'final_base_coords': final_base_coords
        }

        # Schedule session cleanup
        @after_this_request
        def cleanup(response):
            cleanup_old_sessions()
            return response

        return jsonify(response)

    return jsonify({'error': 'File not processed'}), 400

@app.route('/scale_using_reference', methods=['POST'])
def scale_using_reference():
    stick_length = None
    print(request.form)
    if 'image' not in session or 'base_coordinates' not in session:
        print("Session error")
        return jsonify({'error': 'No image available from initiate call'}), 400

    if 'reference_point' not in request.form:
        print("reference_point error")
        return jsonify({'error': 'Reference point not provided'}), 400
    
    if 'stick_length' in request.form:
        try:
            stick_length = float(request.form['stick_length'])
        except ValueError:
            return jsonify({'error': 'stick_length must be a number'}), 400

    reference_point = request.form['reference_point']
    reference_point = tuple(map(int, reference_point.split(',')))  # Convert to tuple of ints

    # print("Using session data")
    # img_array = np.array(session['image_list'])
    img = session['image']

    base_coordinates = session['base_coordinates']
    # print("Done using session data")

    try:
        img, image_scaler_ref = main_script.get_scale_of_image_ref(img, base_coordinates, reference_point,reference_stick_length=stick_length)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Error during scaling: {str(e)}'}), 500

    if image_scaler_ref:
        session['image_scaler'] = image_scaler_ref

   

    response = {
        'reference_used_height': image_scaler_ref.reference['height in inches'],
        'got_scale': image_scaler_ref is not None,
    }

    return jsonify(response)

@app.route('/estimate_height', methods=['POST'])
def estimate_height():
    print('estimate_height',request.form)
    if 'image' not in session or 'base_coordinates' not in session or 'image_scaler' not in session:
        return jsonify({'error': 'Initiate first by uploading an image and base coordinates, and set the scale using reference'}), 400

    if 'height_point' not in request.form:
        return jsonify({'error': 'Height point not provided'}), 400

    height_point = request.form['height_point']
    height_point = tuple(map(int, height_point.split(',')))  # Convert to tuple of ints

    img_array = np.array(session['image'])

    img_scaler = session['image_scaler']

    try:
        height = main_script.get_point_height(img_array, height_point, img_scaler)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Error estimating height: {str(e)}'}), 500

    response = {
        'height': height
    }

    # Schedule session cleanup
    @after_this_request
    def cleanup(response):
        cleanup_old_sessions()
        return response

    return jsonify(response)

# @app.route('/')
# def home():
#     return render_template(r"index.html")

if __name__ == '__main__':
    app.run(debug=True,port=5500)

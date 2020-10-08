import os
import shutil
import json
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_file
from google.cloud import storage
import tensorflow as tf
import tensorflow_hub as hub

app = Flask(__name__)

best_model_id = -1
best_model_name = ""
prediction_model = None
label_names = None
index2label = None

def download_best_model():
    print("Downloading Best Model...")
    # This method download the best model everytime on startup of the server
    best_model_path = "best_model"
    shutil.rmtree(best_model_path, ignore_errors=True)
    os.mkdir(best_model_path)

    # Get GCP project id and bucket from environment variable
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCP_BUCKET = os.environ["GCP_BUCKET"]

    storage_client = storage.Client(project=GCP_PROJECT_ID)
    bucket = storage_client.get_bucket(GCP_BUCKET)
    blobs = bucket.list_blobs(prefix="best_model/", delimiter="/")
    for blob in blobs:
        print(blob)
        blob.download_to_filename(blob.name)

def load_prediction_model():
    print("Loading Model...")
    global prediction_model, label_names, index2label

    # Check if this was a hub model
    with open("best_model/model.json", 'r') as json_file:
        model_json = json.load(json_file)

    layers = model_json["config"]["layers"]
    hub_model = False
    for layer in layers:
        if layer["class_name"] == "KerasLayer":
            hub_model = True
    if hub_model:
        prediction_model = tf.keras.models.load_model('best_model/model.hdf5', custom_objects={'KerasLayer': hub.KerasLayer})
    else:
        prediction_model = tf.keras.models.load_model('best_model/model.hdf5')
    print(prediction_model.summary())

    # Load labels
    with open("best_model/model_metrics.json", 'r') as json_file:
        model_metrics = json.load(json_file)

    label_names = model_metrics["label_names"]
    index2label = dict((index, name) for index, name in enumerate(label_names))

def check_model_change():
    global best_model_id,best_model_name

    GCP_BUCKET = os.environ["GCP_BUCKET"]

    model_metrics_path = "gs://"+GCP_BUCKET+"/best_model/model_metrics.json"

    try:
        with tf.io.gfile.GFile(model_metrics_path) as json_file:
            model_metrics = json.load(json_file)

        if best_model_id != model_metrics["id"]:
            download_best_model()
            load_prediction_model()
            best_model_id = model_metrics["id"]
            best_model_name = model_metrics["name"]
    except:
        print("Could not load model")


@app.route('/')
def root():
    return 'API Server is running!'

@app.route('/model_status')
def model_status():
    # Check for model change
    check_model_change()

    # Check current model being used
    if best_model_name == "":
        return 'No model available to serve'
    else:
        return 'Current model being served: '+ best_model_name

@app.route('/metrics')
def metrics():
    # Check for model change
    check_model_change()

    # Read the model metrics
    with open("best_model/model_metrics.json", 'r') as json_file:
        model_metrics = json.load(json_file)
    return jsonify(model_metrics)

@app.route('/predict')
def predict():
    # Check for model change
    check_model_change()

    file_name = request.args.get('file','test1.jpg')

    # Prepare image for prediction
    predict_x = []
    file_path = "test_images/"+file_name
    # read image
    image = cv2.imread(file_path)
    # convert to rgb
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Reshape
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    predict_x.append(image)

    # Convert to numpy array
    predict_x = np.asarray(predict_x)
    print("predict_x shape:", predict_x.shape)
    print(predict_x[0].shape)

    # Predict
    # Normalization
    predict_x = predict_x.astype("float") / 255.0

    # Make prediction
    prediction = prediction_model.predict(predict_x)
    print(prediction.shape)
    print(prediction)
    prediction = prediction[0].tolist()
    prediction_label = [] #index2label[prediction.argmax(axis=1)[0]]

    for idx,p in enumerate(prediction):
        prediction_label.append({"label":index2label[idx],"value": round(p*100,2)})

    prediction_label.sort(key=lambda x: x["value"], reverse=True)
    prediction_label_html = "<table width='300'>"
    for itm in prediction_label:
        prediction_label_html += "<tr style='font-family: Arial,sans-serif; font-weight: 400; color:#383838;'>"
        prediction_label_html += "<td>" + itm["label"] + "</td><td align='right'>" + str(itm["value"]) + "%</td>"
        prediction_label_html += "</tr>"
    prediction_label_html += "</table>"

    # return jsonify({
    #     "predictions": prediction_label
    # })

    html = ""
    html += "<img src='/get_image?file="+file_name+"' width='300'/>"
    html += "<p>"
    html += prediction_label_html
    html += "</p>"
    html += "<p><small>Prediction made using model:"+best_model_name+"</small></p>"

    return html

@app.route('/get_image')
def get_image():
    file_name = request.args.get('file','test1.jpg')
    file_path = "test_images/" + file_name
    return send_file(file_path, mimetype='image/jpeg')

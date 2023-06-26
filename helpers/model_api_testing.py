from fastapi import UploadFile, File
import tensorflow as tf
import sqlite3
import os
from PIL import Image
import numpy as np
from pydantic import BaseModel
import json

# get json file
with open('class_names.json', 'r') as f:
    json_data = json.load(f)

# our response model
class CropDetectionResponse(BaseModel):
    message: str
    disease: str
    health: str

# import our model
model = tf.keras.models.load_model('model.h5')


# disease labels
class_names = json_data

print(f'class names from json {class_names}')

# function to preprocess our image and make a prediction
def predict_image(image):
    # load our image
    image = tf.keras.preprocessing.image.load_img(image, target_size=(224, 224))
    # preprocess our image
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    # expand the dimensions of our image
    image_array = tf.expand_dims(image_array, 0)
    # make a prediction
    prediction_model = tf.keras.Sequential([
        model,
        tf.keras.layers.Softmax()
    ])
    prediction = prediction_model.predict(image_array)
    # get the index of the highest value and map it to the correct label
    print(f"api predictions {prediction}")
    
    # score = tf.nn.softmax(prediction[0])
    # print(f'score {score}')
    # get maximum value
    max_value = int(tf.argmax(prediction, axis=1).numpy())
    
    print(f"max value {max_value} disease  {class_names[max_value]}")
    
    response_value = "The image is likely a {} with a {:.2f} percentage".format(class_names[max_value], 100 * np.max(max_value))
    print(response_value)
    
    result = class_names[max_value]
    
    # check max value
    if 'healthy' in result:
        return CropDetectionResponse(
            message= 'Crop is in good condition',
            disease='None',
            health='Healthy'
        )
    else:
        return CropDetectionResponse(
            message= response_value,
            disease= result,
            health= 'Unhealthy'
        )
    

# function to save image to sqlite
def save_image_temp(image: UploadFile):
    
    # connect to temp SQLite database
    conn = sqlite3.connect('temp.db')
    # declare cursor to handle queries
    cursor = conn.cursor()
    
    # insert image data to table
    file = cursor.execute(f"INSERT INTO images (name, data) VALUES (?, ?), ({image.filename}, {image.file.read()})")
    
    # get the saved image
    


# function to write uploaded file to disk
def save_image_to_disk_temporary(image: UploadFile, upload_directory):
    # create the directory if it does not exist
    os.makedirs(upload_directory, exist_ok=True)
    
    # save image to disk
    if image.filename:
        image_path = os.path.join(upload_directory, image.filename.lower())

        with open(image_path, 'wb') as f:
            f.write(image.file.read())
        return image_path
    else:
        return None

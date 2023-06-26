from typing import Union
# import fastapi
from fastapi import FastAPI, HTTPException, UploadFile, File
# import pydantic
from pydantic import BaseModel
# import from helpers
from helpers.model_api_testing import predict_image, save_image_to_disk_temporary
import sqlite3
from dotenv import load_dotenv
import os
from datetime import date as Date
from fastapi.staticfiles import StaticFiles

# load environments
load_dotenv()

# get upload directory
upload_directory = os.getenv('UPLOAD_FOLDER')
# get api url
api_url = os.getenv('API_URL')
# script_dir = os.path.dirname(__file__)
# st_abs_file_path = os.path.join(script_dir, "static/")

# create our static directory if it doesn't exist
os.makedirs('static', exist_ok=True)
folder = os.path.dirname(__file__)

# print upload directory
print('Upload directory: ', upload_directory)

# define app
app = FastAPI()

# mount our static directory
app.mount("/static", StaticFiles(directory=folder + "/static"), name="static")



# create our crop model
class Crop(BaseModel):
    name: str
    image: str
    health: str
    dateInspected: Date
    disease: str
    
    
# create our index route for testing purposes
@app.get("/")
def index():
    return {"message": "Hello, world!"}

# create our inspect route to inspect image from post
@app.post("/inspect")
async def inspect(image: UploadFile = File(...)):
    # print the image
    print(f'Image from frontend: {image.filename}')
    
    # save image to disk
    image_path = save_image_to_disk_temporary(image, upload_directory)
    
    # predict image
    prediction = predict_image(image_path)
    
    if (image.filename and image_path and prediction):
        # save to crop model
        crop = Crop(
            name = image.filename,
            image= f'{api_url}{image_path}',
            health= prediction.health,
            dateInspected= Date.today(),
            disease= prediction.disease
        )
        
        return {
            "message": "Successfully inspected crop",
            "crop": crop
        }
    else:
        # return result
        return {
            "message": "Failed to inspect crop",
            "prediction": prediction
        }
    
    

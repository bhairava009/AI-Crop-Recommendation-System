import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

from keras.models import load_model # type: ignore
from keras.preprocessing import image # type: ignore

# Load model safely
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'soil_model.h5')
model = load_model(model_path)

classes = [
    "Black Soil",
    "Cinder Soil",
    "Laterite Soil",
    "Peat Soil",
    "Yellow Soil"
]

def validate_image(file):
    """
    Validates if the file is a proper image.
    """
    if not file or file.filename == '':
        return False
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png']:
        return False
    return True

def predict_soil(img_path):
    """
    Predicts soil type using CNN model.
    """
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    prediction = model.predict(img_array)
    predicted_idx = np.argmax(prediction)
    return classes[predicted_idx]
import numpy as np
import os
import json
import warnings
warnings.filterwarnings('ignore')

from PIL import Image

# Original Soil Types Map
ORIGINAL_SOIL_TYPES = {
    'Clay': 'Clay-rich soils, moisture-retentive',
    'Silt': 'Silt soils, fine particles',
    'Sandy': 'Sandy soils, less fertile',
    'Saline': 'Saline soils, poor fertility',
    'Peaty': 'Peaty soils, organic-rich',
    'Loamy': 'Loamy soils, balanced composition'
}

def get_soil_type_info(soil_type):
    """
    Get information about a soil type.
    """
    return ORIGINAL_SOIL_TYPES.get(soil_type, "Unknown soil type")

def validate_image(file):
    """
    Validates if the file is a proper image.
    """
    if not file or file.filename == '':
        return False
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'avif', 'webp']:
        return False
    return True

# Load Model Globals
cnn_model = None
class_indices = None
inverse_class_indices = {}

def load_models_if_needed():
    global cnn_model, class_indices, inverse_class_indices
    if cnn_model is None:
        try:
            from tensorflow.keras.models import load_model
            base_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
            model_path = os.path.join(base_dir, 'soil_model.h5')
            json_path = os.path.join(base_dir, 'soil_class_indices.json')
            
            if os.path.exists(model_path) and os.path.exists(json_path):
                cnn_model = load_model(model_path)
                with open(json_path, 'r') as f:
                    class_indices = json.load(f)
                # Map integer to class string (e.g., 0 -> "Clay")
                inverse_class_indices = {v: k for k, v in class_indices.items()}
            else:
                print("CNN model or class mapping JSON not found.")
        except Exception as e:
            print(f"Error loading CNN model: {e}")

def predict_soil(img_path):
    """
    Predicts soil type using trained CNN Keras model.
    """
    load_models_if_needed()
    
    if cnn_model is None or not inverse_class_indices:
        return "Error: CNN model or class mapping not found"
        
    try:
        from tensorflow.keras.preprocessing import image
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        
        # Load image and resize to (150, 150)
        img = image.load_img(img_path, target_size=(150, 150))
        img_array = image.img_to_array(img)
        
        # Expand dims to create a batch of 1
        img_batch = np.expand_dims(img_array, axis=0)
        
        # Preprocess exactly as MobileNetV2 expects (range -1 to 1)
        img_batch = preprocess_input(img_batch)
        
        # Predict
        prediction = cnn_model.predict(img_batch, verbose=0)
        max_prob = float(np.max(prediction[0]))
        predicted_class_idx = np.argmax(prediction[0])
        
        # Confidence Threshold Check to reject non-soil images
        if max_prob < 0.50:
            return "Not a Soil Image"
        
        # Map back to string
        predicted_label = inverse_class_indices.get(predicted_class_idx, "Unknown")
        return predicted_label
        
    except Exception as e:
        print(f"Error during CNN prediction: {e}")
        return "Error: Prediction failed"
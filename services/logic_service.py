import pickle
import numpy as np
import os

base_dir = os.path.join(os.path.dirname(__file__), '..', 'models')

# Load npk model and label encoder
npk_model_path = os.path.join(base_dir, 'npk_model.pkl')
label_encoder_path = os.path.join(base_dir, 'label_encoder.pkl')

if os.path.exists(npk_model_path) and os.path.exists(label_encoder_path):
    with open(npk_model_path, 'rb') as f:
        npk_model = pickle.load(f)
    with open(label_encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)
else:
    npk_model = None
    label_encoder = None

def predict_npk(soil_type):
    """
    Predicts realistic baseline NPK values based on the soil type
    and adds a strictly bounded variance (±15%) for robust dynamic outputs.
    """
    if not npk_model or not label_encoder:
        return 50, 50, 50
        
    try:
        soil_enc = label_encoder.transform([soil_type])[0]
        
        # Predict the robust median baseline for this soil type
        npk = npk_model.predict([[soil_enc]])[0]
        
        # Apply a bounded 15% variance to ensure variety without breaking agricultural limits
        baseline_n = npk[0] * np.random.uniform(0.85, 1.15)
        baseline_p = npk[1] * np.random.uniform(0.85, 1.15)
        baseline_k = npk[2] * np.random.uniform(0.85, 1.15)
        
        return int(baseline_n), int(baseline_p), int(baseline_k)
    except Exception as e:
        print("Error predicting NPK:", e)
        # Fallback if unknown soil type or error
        return 50, 50, 50

def apply_previous_crop_logic(top_crops, previous_crop):
    """
    Reduces the probability of the previous crop by 50% to encourage crop rotation.
    top_crops is a list of tuples: (crop_name, probability)
    """
    if not previous_crop or previous_crop.strip() == "":
        return top_crops
        
    adjusted_crops = []
    prev = previous_crop.lower().strip()
    
    for crop, prob in top_crops:
        if crop.lower().strip() == prev:
            # Reduce probability by 50%
            adjusted_crops.append((crop, round(prob * 0.5, 2)))
        else:
            adjusted_crops.append((crop, prob))
            
    # Re-sort descending
    adjusted_crops.sort(key=lambda x: x[1], reverse=True)
    return adjusted_crops

def classify_weather(temp, humidity, rainfall):
    """
    Classifies the weather as Dry, Rainy, or Moderate.
    """
    if rainfall < 10 and humidity < 60:
        return "Dry"
    elif rainfall > 30 or humidity > 80:
        return "Rainy"
    else:
        return "Moderate"
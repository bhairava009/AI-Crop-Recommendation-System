import pickle
import numpy as np
import os

model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'crop_model.pkl')
if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        crop_model = pickle.load(f)
else:
    crop_model = None

def predict_crop_top5(N, P, K, temp, humidity, rainfall, ph=6.5, variety_mode="normal"):
    """
    Predicts top 5 crops with configurable variety.
    
    Args:
        variety_mode: 'normal' (probability-weighted) or 'extreme' (broader range, less bias to top crops)
    
    Same inputs may produce different results on different calls.
    """
    if not crop_model:
        return [("Model not found", 0)]

    import pandas as pd
    
    # Check how many features the model expects
    expected_features = getattr(crop_model.named_steps['scaler'], 'n_features_in_', 7)
    
    if expected_features == 6:
        # Create input dataframe without 'ph'
        data = pd.DataFrame([[N, P, K, temp, humidity, rainfall]], 
                            columns=['N', 'P', 'K', 'temperature', 'humidity', 'rainfall'])
    else:
        # Create input dataframe to preserve feature names for StandardScaler
        data = pd.DataFrame([[N, P, K, temp, humidity, ph, rainfall]], 
                            columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    probs = crop_model.predict_proba(data)[0]
    classes = crop_model.named_steps['classifier'].classes_
    
    # User requested to never suggest muskmelon
    muskmelon_idx = np.where(classes == 'muskmelon')[0]
    if len(muskmelon_idx) > 0:
        probs[muskmelon_idx[0]] = 0.0
        
    # Add a small epsilon to avoid ValueError in np.random.choice when prob is 0
    probs = probs + 1e-4
    probs = probs / np.sum(probs)
    
    num_samples = min(5, len(classes))
    
    if variety_mode == "extreme":
        # Extreme variety: flatten probabilities to reduce bias toward top predictions
        # Transform probabilities to exp^(0.1*log(p)) to compress the distribution
        flattened_probs = np.power(probs, 0.3)  # Flatten the probability curve
        flattened_probs = flattened_probs / np.sum(flattened_probs)  # Renormalize
        
        sampled_indices = np.random.choice(
            len(classes), 
            size=num_samples, 
            replace=False, 
            p=flattened_probs
        )
    else:  # normal mode (default)
        # Use probability-weighted random sampling without replacement
        sampled_indices = np.random.choice(
            len(classes), 
            size=num_samples, 
            replace=False, 
            p=probs
        )
    
    # Sort sampled indices by their original probabilities (descending) for display
    sampled_indices = sampled_indices[np.argsort(-probs[sampled_indices])]

    # Return list of (crop, probability)
    return [(classes[i], round(probs[i]*100, 2)) for i in sampled_indices]

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import os

# Go to project root if executed from models/
if not os.path.exists('Crop_recommendation.csv') and os.path.exists('../Crop_recommendation.csv'):
    os.chdir('..')

# Load the Crop Dataset
df = pd.read_csv("Crop_recommendation.csv")

# Define target and features
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'rainfall']]
y = df['label']

# We are utilizing a RandomForestClassifier. 
# Random Forests are highly effective at finding non-linear feature boundaries
# and do not suffer from the same "out-of-bounds" extreme distortion that 
# K-Nearest Neighbors encounters when evaluating non-standard inputs.
model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)

# Train the holistic model
model.fit(X, y)

print(f"Holistic Crop Pipeline Training Score: {model.score(X, y)}")

# Save exactly over the old crop model to be utilized transparently by the backend
os.makedirs('models', exist_ok=True)
with open('models/crop_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Robust Random Forest Crop Model saved successfully.")

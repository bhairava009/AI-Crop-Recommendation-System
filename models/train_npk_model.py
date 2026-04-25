import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Go to project root if executed from models/
if not os.path.exists('npk_soil_dataset.csv') and os.path.exists('../npk_soil_dataset.csv'):
    os.chdir('..')

# Load dataset
df = pd.read_csv("npk_soil_dataset.csv")

# Encode Soil_Type
le = LabelEncoder()
df['Soil_Type_Encoded'] = le.fit_transform(df['Soil_Type'])

# Features focused entirely on Soil_Type 
# (The model naturally converges on mean/median NPK clusters per soil!)
X = df[['Soil_Type_Encoded']]
y = df[['Nitrogen', 'Phosphorus', 'Potassium']]

# Train model 
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, y)

print(f"NPK Base Mapping Model Training R^2 Score: {model.score(X, y)}")

# Save model and encoder
os.makedirs('models', exist_ok=True)
with open('models/npk_model.pkl', 'wb') as f:
    pickle.dump(model, f)
    
with open('models/label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("Realistic NPK Base Model saved successfully in models/")

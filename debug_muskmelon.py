import pandas as pd

df = pd.read_csv("Crop_recommendation.csv")
muskmelon = df[df['label'] == 'muskmelon']
print(muskmelon.describe())
